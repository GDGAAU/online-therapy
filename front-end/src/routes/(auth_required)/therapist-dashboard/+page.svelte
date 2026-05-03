<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { ApiError, therapyApi } from '$lib/api';
  import { authStore } from '$lib/stores/auth';
  import { Button } from '$lib/components/ui/button';
  import TherapistCalendar from '$lib/components/booking/TherapistCalendar.svelte';
  import type { Appointment, Specialty, Therapist } from '$lib/types';
  import {
    adaptAvailability,
    formatDateKey,
    formatDateTime,
    formatExperience,
    formatFee,
    formatSessionType
  } from '$lib/utils/therapy';
  import type { TimeSlot } from '$lib/components/booking/TherapistCalendar.svelte';

  const availabilityWindowDays = 35;

  let therapist = $state<Therapist | null>(null);
  let sessions = $state<Appointment[]>([]);
  let specialties = $state<Specialty[]>([]);
  let availability = $state<Record<string, TimeSlot[]>>({});

  let selectedDate = $state('');
  let selectedSlotId = $state('');
  let isLoading = $state(true);
  let isProfileSaving = $state(false);
  let actionInProgress = $state('');
  let loadError = $state('');

  let bio = $state('');
  let licenseNumber = $state('');
  let consultationFee = $state('');
  let yearsOfExperience = $state(0);
  let isAvailable = $state(true);
  let selectedSpecialtySlugs = $state<string[]>([]);

  let upcomingSessions = $derived(
    sessions
      .filter((session) => ['pending', 'confirmed'].includes(session.status))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))
  );

  let todayCount = $derived(
    sessions.filter((session) => formatDateKey(new Date(session.scheduled_at)) === formatDateKey(new Date())).length
  );
  let pendingCount = $derived(sessions.filter((session) => session.status === 'pending').length);
  let confirmedCount = $derived(sessions.filter((session) => session.status === 'confirmed').length);
  let completedCount = $derived(sessions.filter((session) => session.status === 'completed').length);

  let selectedSlot = $derived(
    selectedDate
      ? (availability[selectedDate] ?? []).find((slot) => slot.id === selectedSlotId) ?? null
      : null
  );

  let selectedDateLabel = $derived(
    selectedDate
      ? new Intl.DateTimeFormat('en-US', {
          weekday: 'long',
          month: 'short',
          day: 'numeric'
        }).format(new Date(`${selectedDate}T00:00:00`))
      : 'No date selected'
  );

  function hydrateProfileForm(nextTherapist: Therapist) {
    bio = nextTherapist.bio ?? '';
    licenseNumber = nextTherapist.license_number ?? '';
    consultationFee = nextTherapist.consultation_fee ?? '';
    yearsOfExperience = nextTherapist.years_of_experience;
    isAvailable = nextTherapist.is_available;
    selectedSpecialtySlugs = nextTherapist.specialties.map((specialty) => specialty.slug);
  }

  function getPatientName(session: Appointment) {
    return session.patient_name || session.patient_email || 'Patient';
  }

  function statusBadgeClass(status: Appointment['status']) {
    if (status === 'confirmed') return 'bg-emerald-100 text-emerald-700';
    if (status === 'pending') return 'bg-amber-100 text-amber-700';
    if (status === 'completed') return 'bg-blue-100 text-blue-700';
    return 'bg-rose-100 text-rose-700';
  }

  function toggleSpecialty(slug: string) {
    selectedSpecialtySlugs = selectedSpecialtySlugs.includes(slug)
      ? selectedSpecialtySlugs.filter((item) => item !== slug)
      : [...selectedSpecialtySlugs, slug];
  }

  async function loadAvailability(therapistId: string) {
    const from = new Date();
    const to = new Date(from.getFullYear(), from.getMonth(), from.getDate() + availabilityWindowDays);
    const response = await therapyApi.getTherapistAvailability(
      therapistId,
      formatDateKey(from),
      formatDateKey(to)
    );
    availability = adaptAvailability(response);
  }

  async function loadDashboard() {
    isLoading = true;
    loadError = '';

    try {
      const profile = await therapyApi.getCurrentTherapistProfile();
      therapist = profile;
      hydrateProfileForm(profile);

      const [sessionResponse, specialtyResponse] = await Promise.all([
        therapyApi.listAppointments(undefined, 'therapist'),
        therapyApi.listSpecialties(),
        loadAvailability(profile.id)
      ]);

      sessions = sessionResponse.results;
      specialties = specialtyResponse.results;
    } catch (err) {
      loadError = err instanceof ApiError ? err.message : 'Failed to load therapist workspace.';
    } finally {
      isLoading = false;
    }
  }

  async function saveProfile() {
    isProfileSaving = true;

    try {
      const updated = await therapyApi.updateCurrentTherapistProfile({
        bio: bio.trim(),
        license_number: licenseNumber.trim(),
        consultation_fee: consultationFee.trim() || null,
        years_of_experience: Number(yearsOfExperience) || 0,
        is_available: isAvailable,
        specialties: selectedSpecialtySlugs
      });

      therapist = updated;
      hydrateProfileForm(updated);
      toast.success('Therapist profile updated.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to update therapist profile.');
    } finally {
      isProfileSaving = false;
    }
  }

  async function refreshSessions() {
    const response = await therapyApi.listAppointments(undefined, 'therapist');
    sessions = response.results;
  }

  async function confirmSession(sessionId: string) {
    actionInProgress = `confirm:${sessionId}`;

    try {
      await therapyApi.confirmAppointment(sessionId);
      await refreshSessions();
      toast.success('Session confirmed.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to confirm session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function completeSession(sessionId: string) {
    actionInProgress = `complete:${sessionId}`;

    try {
      await therapyApi.completeAppointment(sessionId);
      await refreshSessions();
      toast.success('Session marked complete.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to complete session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function cancelSession(sessionId: string) {
    actionInProgress = `cancel:${sessionId}`;

    try {
      await therapyApi.cancelAppointment(sessionId, 'Cancelled by therapist');
      await refreshSessions();
      if (therapist) await loadAvailability(therapist.id);
      toast.success('Session cancelled.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to cancel session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function generateMeetingLink(sessionId: string) {
    actionInProgress = `meeting:${sessionId}`;

    try {
      const response = await therapyApi.generateMeetingLink(sessionId);
      sessions = sessions.map((session) =>
        session.id === sessionId ? { ...session, meeting_link: response.meeting_link } : session
      );
      toast.success('Meeting link ready.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to generate meeting link.');
    } finally {
      actionInProgress = '';
    }
  }

  onMount(() => {
    void loadDashboard();
  });
</script>

<svelte:head>
  <title>Therapist Dashboard - Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  {#if isLoading}
    <div class="grid gap-4 sm:grid-cols-3" aria-live="polite">
      {#each Array(6) as _, index (index)}
        <article class="h-32 animate-pulse rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <div class="h-4 w-24 rounded bg-blue-100"></div>
          <div class="mt-4 h-8 w-16 rounded bg-blue-50"></div>
        </article>
      {/each}
    </div>
  {:else if loadError}
    <section class="rounded-lg border border-rose-200 bg-rose-50 p-6">
      <h1 class="text-lg font-semibold text-rose-900">Unable to load therapist workspace</h1>
      <p class="mt-2 text-sm text-rose-700">{loadError}</p>
      <Button class="mt-4 bg-blue-600 text-white hover:bg-blue-700" onclick={loadDashboard}>Retry</Button>
    </section>
  {:else if therapist}
    <header class="rounded-lg border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
      <p class="text-xs font-semibold uppercase tracking-wide text-blue-500">Therapist Workspace</p>
      <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">
            Welcome, {$authStore.user?.first_name || therapist.name}
          </h1>
          <p class="mt-1 text-sm text-slate-600">
            {therapist.specialties.length > 0
              ? therapist.specialties.map((specialty) => specialty.name).join(' / ')
              : 'Specialties pending'}
            {therapist.license_number ? ` / License ${therapist.license_number}` : ''}
          </p>
        </div>
        <div class="rounded-lg border border-blue-100 bg-white px-4 py-3 text-sm text-slate-700">
          <p><span class="font-medium text-blue-900">Fee:</span> {formatFee(therapist.consultation_fee)}</p>
          <p><span class="font-medium text-blue-900">Experience:</span> {formatExperience(therapist.years_of_experience)}</p>
        </div>
      </div>
    </header>

    {#if therapist.is_profile_complete === false}
      <section class="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        <p class="font-semibold">Profile needs attention</p>
        <p class="mt-1">Bio, specialties, license number, and consultation fee are required for a complete therapist profile.</p>
      </section>
    {/if}

    <div class="grid gap-4 sm:grid-cols-4">
      <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Today</p>
        <p class="mt-2 text-2xl font-semibold text-blue-900">{todayCount}</p>
      </article>
      <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Pending</p>
        <p class="mt-2 text-2xl font-semibold text-amber-600">{pendingCount}</p>
      </article>
      <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Confirmed</p>
        <p class="mt-2 text-2xl font-semibold text-emerald-700">{confirmedCount}</p>
      </article>
      <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Completed</p>
        <p class="mt-2 text-2xl font-semibold text-blue-700">{completedCount}</p>
      </article>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
      <section class="space-y-4 rounded-lg border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold text-blue-900">Session Pipeline</h2>
          <Button variant="outline" class="border-blue-200 text-blue-700" onclick={refreshSessions}>
            Refresh
          </Button>
        </div>

        {#if sessions.length === 0}
          <p class="rounded-lg border border-dashed border-blue-200 p-4 text-sm text-slate-500">
            No sessions yet. New therapist appointments will appear here.
          </p>
        {:else}
          <div class="space-y-3">
            {#each sessions as session (session.id)}
              <article class="rounded-lg border border-slate-200 p-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 class="font-medium text-blue-950">{getPatientName(session)}</h3>
                    <p class="text-sm text-slate-600">
                      {formatDateTime(session.scheduled_at)} / {session.duration_minutes} min / {formatSessionType(session.appointment_type)}
                    </p>
                  </div>
                  <span class={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusBadgeClass(session.status)}`}>
                    {session.status}
                  </span>
                </div>

                {#if session.reason}
                  <p class="mt-2 text-sm text-slate-700">{session.reason}</p>
                {/if}

                <div class="mt-3 flex flex-wrap gap-2">
                  {#if session.status === 'pending'}
                    <Button
                      class="bg-blue-600 text-white hover:bg-blue-700"
                      onclick={() => confirmSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `confirm:${session.id}` ? 'Confirming...' : 'Confirm'}
                    </Button>
                  {/if}

                  {#if session.status === 'confirmed'}
                    <Button
                      variant="outline"
                      class="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                      onclick={() => completeSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `complete:${session.id}` ? 'Saving...' : 'Mark complete'}
                    </Button>
                    <Button
                      variant="outline"
                      class="border-rose-300 text-rose-700 hover:bg-rose-50"
                      onclick={() => cancelSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `cancel:${session.id}` ? 'Cancelling...' : 'Cancel'}
                    </Button>
                    <Button
                      variant="outline"
                      class="border-blue-300 text-blue-700 hover:bg-blue-50"
                      onclick={() => generateMeetingLink(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `meeting:${session.id}` ? 'Preparing...' : session.meeting_link ? 'Refresh meeting link' : 'Generate meeting link'}
                    </Button>
                  {/if}

                  {#if session.meeting_link}
                    <a href={session.meeting_link} target="_blank" rel="noreferrer" class="inline-flex">
                      <Button variant="outline" class="border-blue-200 text-blue-700 hover:bg-blue-50">
                        Open meeting
                      </Button>
                    </a>
                  {/if}
                </div>
              </article>
            {/each}
          </div>
        {/if}
      </section>

      <section class="space-y-4">
        <TherapistCalendar bind:selectedDate bind:selectedSlot={selectedSlotId} {availability} />

        <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <h3 class="text-sm font-semibold text-blue-900">Selected availability slot</h3>
          <p class="mt-2 text-sm text-slate-700">Date: {selectedDateLabel}</p>
          <p class="text-sm text-slate-700">
            Time: {selectedSlot ? `${selectedSlot.time} (${selectedSlot.duration_minutes} min)` : 'No slot selected'}
          </p>
        </article>

        <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <h3 class="text-sm font-semibold text-blue-900">Upcoming Sessions</h3>
          <ul class="mt-3 space-y-2 text-sm text-slate-700">
            {#each upcomingSessions.slice(0, 3) as upcoming (upcoming.id)}
              <li class="rounded-lg bg-blue-50 px-3 py-2">
                <p class="font-medium text-blue-900">{getPatientName(upcoming)}</p>
                <p>{formatDateTime(upcoming.scheduled_at)}</p>
              </li>
            {/each}
            {#if upcomingSessions.length === 0}
              <li class="rounded-lg border border-dashed border-blue-200 px-3 py-2 text-slate-500">
                No upcoming sessions.
              </li>
            {/if}
          </ul>
        </article>
      </section>
    </div>

    <section class="space-y-4 rounded-lg border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-lg font-semibold text-blue-900">Profile Settings</h2>
        <Button class="bg-blue-600 text-white hover:bg-blue-700" onclick={saveProfile} disabled={isProfileSaving}>
          {isProfileSaving ? 'Saving...' : 'Save profile'}
        </Button>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <label class="space-y-1 text-sm">
          <span class="font-medium text-blue-900">License number</span>
          <input
            bind:value={licenseNumber}
            class="h-11 w-full rounded-lg border border-blue-200 px-3 text-sm outline-none focus:border-blue-500"
            placeholder="License number"
          />
        </label>

        <label class="space-y-1 text-sm">
          <span class="font-medium text-blue-900">Consultation fee</span>
          <input
            bind:value={consultationFee}
            class="h-11 w-full rounded-lg border border-blue-200 px-3 text-sm outline-none focus:border-blue-500"
            inputmode="decimal"
            placeholder="150.00"
          />
        </label>

        <label class="space-y-1 text-sm">
          <span class="font-medium text-blue-900">Years of experience</span>
          <input
            bind:value={yearsOfExperience}
            class="h-11 w-full rounded-lg border border-blue-200 px-3 text-sm outline-none focus:border-blue-500"
            min="0"
            type="number"
          />
        </label>

        <label class="flex items-center gap-3 rounded-lg border border-blue-100 px-3 py-3 text-sm text-blue-900">
          <input type="checkbox" bind:checked={isAvailable} class="h-4 w-4 rounded border-blue-300" />
          Accepting new clients
        </label>
      </div>

      <label class="block space-y-1 text-sm">
        <span class="font-medium text-blue-900">Bio</span>
        <textarea
          bind:value={bio}
          rows="4"
          class="w-full rounded-lg border border-blue-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
          placeholder="Therapist bio"
        ></textarea>
      </label>

      <div class="space-y-2">
        <p class="text-sm font-medium text-blue-900">Specialties</p>
        <div class="flex flex-wrap gap-2">
          {#each specialties as specialty (specialty.id)}
            <button
              type="button"
              aria-pressed={selectedSpecialtySlugs.includes(specialty.slug)}
              class={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                selectedSpecialtySlugs.includes(specialty.slug)
                  ? 'border-blue-600 bg-blue-600 text-white'
                  : 'border-blue-100 bg-white text-blue-700 hover:bg-blue-50'
              }`}
              onclick={() => toggleSpecialty(specialty.slug)}
            >
              {specialty.name}
            </button>
          {/each}
        </div>
      </div>
    </section>
  {/if}
</section>
