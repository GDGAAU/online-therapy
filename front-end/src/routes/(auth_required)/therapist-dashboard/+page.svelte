<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { Button } from '$lib/components/ui/button';
  import TherapistCalendar from '$lib/components/booking/TherapistCalendar.svelte';
  import {
    buildMockAvailability,
    defaultMockTherapistId,
    mockTherapistsById,
    type MockAvailabilitySlot,
    type MockTherapistDetail
  } from '$lib/mock/therapist-booking';

  type TherapistAppointmentStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled';
  type TherapistAppointmentType = 'video' | 'in_person' | 'phone';

  interface TherapistSession {
    id: string;
    patient_name: string;
    status: TherapistAppointmentStatus;
    appointment_type: TherapistAppointmentType;
    scheduled_at: string;
    duration_minutes: number;
    reason: string;
    meeting_link?: string | null;
  }

  let therapist = $state<MockTherapistDetail>(mockTherapistsById[defaultMockTherapistId]);
  let availability = $state<Record<string, MockAvailabilitySlot[]>>(buildMockAvailability(new Date(), 42));

  let selectedDate = $state('');
  let selectedSlotId = $state('');

  const sessionsSeed: TherapistSession[] = [
    {
      id: 'sess-1',
      patient_name: 'Mia Parker',
      status: 'confirmed',
      appointment_type: 'video',
      scheduled_at: new Date(Date.now() + 1000 * 60 * 60 * 2).toISOString(),
      duration_minutes: 50,
      reason: 'Anxiety and stress management',
      meeting_link: 'https://meet.google.com/abc-defg-hij'
    },
    {
      id: 'sess-2',
      patient_name: 'Daniel Brooks',
      status: 'pending',
      appointment_type: 'in_person',
      scheduled_at: new Date(Date.now() + 1000 * 60 * 60 * 26).toISOString(),
      duration_minutes: 50,
      reason: 'Sleep disturbance and work burnout',
      meeting_link: null
    },
    {
      id: 'sess-3',
      patient_name: 'Leila Ahmed',
      status: 'completed',
      appointment_type: 'phone',
      scheduled_at: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
      duration_minutes: 30,
      reason: 'Follow-up after panic episode',
      meeting_link: null
    }
  ];

  let sessions = $state<TherapistSession[]>(sessionsSeed);

  let upcomingSessions = $derived(
    sessions
      .filter((s) => ['pending', 'confirmed'].includes(s.status))
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))
  );

  let todayCount = $derived(
    sessions.filter((s) => {
      const d = new Date(s.scheduled_at);
      const now = new Date();
      return (
        d.getFullYear() === now.getFullYear() &&
        d.getMonth() === now.getMonth() &&
        d.getDate() === now.getDate()
      );
    }).length
  );

  let pendingCount = $derived(sessions.filter((s) => s.status === 'pending').length);
  let completedCount = $derived(sessions.filter((s) => s.status === 'completed').length);

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

  function formatDateTime(iso: string) {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(iso));
  }

  function markSessionCompleted(sessionId: string) {
    sessions = sessions.map((session) =>
      session.id === sessionId ? { ...session, status: 'completed' } : session
    );
  }

  function acceptPendingSession(sessionId: string) {
    sessions = sessions.map((session) =>
      session.id === sessionId ? { ...session, status: 'confirmed' } : session
    );
  }

  function statusBadgeClass(status: TherapistAppointmentStatus) {
    if (status === 'confirmed') return 'bg-emerald-100 text-emerald-700';
    if (status === 'pending') return 'bg-amber-100 text-amber-700';
    if (status === 'completed') return 'bg-blue-100 text-blue-700';
    return 'bg-rose-100 text-rose-700';
  }
</script>

<svelte:head>
  <title>Therapist Dashboard — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Therapist Workspace</p>
    <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">
          Welcome, {$authStore.user?.first_name || therapist.name}
        </h1>
        <p class="mt-1 text-sm text-slate-600">
          {therapist.specialties.map((s) => s.name).join(' • ')} • License {therapist.license_number}
        </p>
      </div>
      <div class="rounded-xl border border-blue-100 bg-white px-4 py-3 text-sm text-slate-700">
        <p><span class="font-medium text-blue-900">Fee:</span> ${therapist.consultation_fee ?? '0.00'}</p>
        <p><span class="font-medium text-blue-900">Experience:</span> {therapist.years_of_experience} years</p>
      </div>
    </div>
  </header>

  <div class="grid gap-4 sm:grid-cols-3">
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Today’s sessions</p>
      <p class="mt-2 text-2xl font-semibold text-blue-900">{todayCount}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Pending approvals</p>
      <p class="mt-2 text-2xl font-semibold text-amber-600">{pendingCount}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Completed sessions</p>
      <p class="mt-2 text-2xl font-semibold text-emerald-700">{completedCount}</p>
    </article>
  </div>

  <div class="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
    <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-blue-900">Session Pipeline</h2>
        <span class="text-xs text-slate-500">Backend-compatible mock state</span>
      </div>

      {#if sessions.length === 0}
        <p class="rounded-xl border border-dashed border-blue-200 p-4 text-sm text-slate-500">
          No sessions yet. New therapist appointments will appear here.
        </p>
      {:else}
        <div class="space-y-3">
          {#each sessions as session (session.id)}
            <article class="rounded-xl border border-slate-200 p-4">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 class="font-medium text-blue-950">{session.patient_name}</h3>
                  <p class="text-sm text-slate-600">{formatDateTime(session.scheduled_at)} • {session.duration_minutes} min • {session.appointment_type}</p>
                </div>
                <span class={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusBadgeClass(session.status)}`}>
                  {session.status}
                </span>
              </div>

              <p class="mt-2 text-sm text-slate-700">{session.reason}</p>

              <div class="mt-3 flex flex-wrap gap-2">
                {#if session.status === 'pending'}
                  <Button class="bg-blue-600 text-white hover:bg-blue-700" onclick={() => acceptPendingSession(session.id)}>
                    Accept session
                  </Button>
                {/if}

                {#if session.status === 'confirmed'}
                  <Button variant="outline" class="border-emerald-300 text-emerald-700 hover:bg-emerald-50" onclick={() => markSessionCompleted(session.id)}>
                    Mark completed
                  </Button>
                {/if}

                {#if session.meeting_link}
                  <a href={session.meeting_link} target="_blank" rel="noreferrer" class="inline-flex">
                    <Button variant="outline" class="border-blue-200 text-blue-700 hover:bg-blue-50">
                      Open meeting link
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

      <article class="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm">
        <h3 class="text-sm font-semibold text-blue-900">Selected scheduling slot</h3>
        <p class="mt-2 text-sm text-slate-700">Date: {selectedDateLabel}</p>
        <p class="text-sm text-slate-700">
          Time: {selectedSlot ? `${selectedSlot.time} (${selectedSlot.duration_minutes} min)` : 'No slot selected'}
        </p>
      </article>

      <article class="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm">
        <h3 class="text-sm font-semibold text-blue-900">Upcoming Sessions</h3>
        <ul class="mt-3 space-y-2 text-sm text-slate-700">
          {#each upcomingSessions.slice(0, 3) as upcoming (upcoming.id)}
            <li class="rounded-lg bg-blue-50 px-3 py-2">
              <p class="font-medium text-blue-900">{upcoming.patient_name}</p>
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
</section>
