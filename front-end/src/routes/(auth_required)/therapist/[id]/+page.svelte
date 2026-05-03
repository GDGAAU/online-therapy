<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { ApiError, therapyApi } from '$lib/api';
  import { Button } from '$lib/components/ui/button';
  import TherapistCalendar, { type TimeSlot } from '$lib/components/booking/TherapistCalendar.svelte';
  import type { AppointmentType, Therapist, TherapistAvailabilitySlot } from '$lib/types';

  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  const availabilityWindowDays = 35;

  let isLoading = $state(true);
  let isAvailabilityLoading = $state(false);
  let isSubmitting = $state(false);
  let bookingSuccess = $state(false);
  let notFound = $state(false);
  let loadError = $state('');
  let bookingError = $state('');

  let therapist = $state<Therapist | null>(null);
  let availability = $state<Record<string, TimeSlot[]>>({});

  let selectedDate = $state('');
  let selectedSlotId = $state('');
  let selectedType = $state<AppointmentType>('video');
  let reason = $state('');
  let redirectTimer: ReturnType<typeof setTimeout> | null = null;

  let selectedSlot = $derived(
    selectedDate
      ? (availability[selectedDate] ?? []).find((slot) => slot.id === selectedSlotId) ?? null
      : null
  );

  let payloadPreview = $derived(
    therapist && selectedSlot
      ? {
          therapist_id: therapist.id,
          scheduled_at: selectedSlot.startAt,
          appointment_type: selectedType,
          reason: reason.trim()
        }
      : null
  );

  let selectedDateLabel = $derived(
    selectedDate
      ? new Intl.DateTimeFormat('en-US', {
          weekday: 'long',
          month: 'long',
          day: 'numeric'
        }).format(new Date(`${selectedDate}T00:00:00`))
      : 'Choose a date'
  );

  let canBook = $derived(Boolean(payloadPreview?.scheduled_at && therapist?.is_available));

  let formattedFee = $derived(formatFee(therapist?.consultation_fee ?? null));

  function formatDateKey(date: Date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function formatFee(fee: string | null) {
    if (!fee) return 'Fee on request';

    const amount = Number.parseFloat(fee);

    if (!Number.isFinite(amount)) return `USD ${fee}`;

    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: amount % 1 === 0 ? 0 : 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  function formatExperience(years: number) {
    return `${years} ${years === 1 ? 'year' : 'years'} experience`;
  }

  function formatTime(value: string) {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(value));
  }

  function getDurationMinutes(slot: TherapistAvailabilitySlot) {
    const start = new Date(slot.start_at).getTime();
    const end = new Date(slot.end_at).getTime();
    const duration = Math.round((end - start) / 60_000);
    return Number.isFinite(duration) && duration > 0 ? duration : 50;
  }

  function adaptAvailability(
    response: Record<string, TherapistAvailabilitySlot[]>
  ): Record<string, TimeSlot[]> {
    return Object.fromEntries(
      Object.entries(response).map(([date, slots]) => [
        date,
        slots.map((slot, index) => ({
          id: `${slot.start_at}-${index}`,
          time: formatTime(slot.start_at),
          status: slot.is_available ? 'available' : 'booked',
          startAt: slot.start_at,
          duration_minutes: getDurationMinutes(slot)
        }))
      ])
    );
  }

  async function loadAvailability(therapistId: string) {
    isAvailabilityLoading = true;

    try {
      const from = new Date();
      const to = new Date(from.getFullYear(), from.getMonth(), from.getDate() + availabilityWindowDays);
      const response = await therapyApi.getTherapistAvailability(
        therapistId,
        formatDateKey(from),
        formatDateKey(to)
      );

      availability = adaptAvailability(response);
    } catch (err) {
      loadError = err instanceof ApiError ? err.message : 'Failed to load therapist availability.';
    } finally {
      isAvailabilityLoading = false;
    }
  }

  onMount(async () => {
    const therapistId = $page.params.id;

    if (!therapistId || !uuidPattern.test(therapistId)) {
      notFound = true;
      isLoading = false;
      return;
    }

    try {
      const [therapistResponse] = await Promise.all([
        therapyApi.getTherapist(therapistId),
        loadAvailability(therapistId)
      ]);

      therapist = therapistResponse;
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        notFound = true;
      } else {
        loadError = err instanceof ApiError ? err.message : 'Failed to load therapist profile.';
      }
    } finally {
      isLoading = false;
    }
  });

  onDestroy(() => {
    if (redirectTimer) clearTimeout(redirectTimer);
  });

  async function bookSession() {
    if (!canBook || !payloadPreview) return;

    isSubmitting = true;
    bookingError = '';
    bookingSuccess = false;

    try {
      await therapyApi.createAppointment({
        therapist_id: payloadPreview.therapist_id,
        scheduled_at: new Date(payloadPreview.scheduled_at).toISOString(),
        appointment_type: payloadPreview.appointment_type,
        reason: payloadPreview.reason
      });

      bookingSuccess = true;
      toast.success('Session booked successfully.');

      redirectTimer = setTimeout(() => {
        goto('/appointment');
      }, 2000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        bookingError = 'That time was just booked. Choose another available slot.';
        if (therapist) await loadAvailability(therapist.id);
      } else {
        bookingError = err instanceof ApiError ? err.message : 'Failed to book this session.';
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>{therapist ? `${therapist.name} - Booking` : 'Therapist Profile'} - Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-6xl space-y-6 p-4 pb-12 sm:p-6 lg:p-8">
  <div class="flex items-center justify-between">
    <Button
      variant="outline"
      class="border-blue-200 text-blue-700 hover:bg-blue-50"
      onclick={() => goto('/book-appointment')}
    >
      Back to therapists
    </Button>
  </div>

  {#if isLoading}
    <article class="grid gap-6 lg:grid-cols-[1.15fr_1fr]" aria-live="polite">
      <div class="animate-pulse space-y-4 rounded-lg border border-blue-100 bg-white p-6">
        <div class="h-6 w-52 rounded bg-blue-100"></div>
        <div class="h-4 w-40 rounded bg-blue-50"></div>
        <div class="h-24 rounded-lg bg-blue-50"></div>
      </div>
      <div class="animate-pulse rounded-lg border border-blue-100 bg-white p-6">
        <div class="h-8 w-44 rounded bg-blue-100"></div>
        <div class="mt-4 h-56 rounded-lg bg-blue-50"></div>
      </div>
    </article>
  {:else if notFound}
    <section class="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
      <p class="text-sm font-semibold uppercase tracking-wide text-blue-500">404</p>
      <h1 class="mt-2 text-2xl font-semibold text-slate-950">Therapist not found</h1>
      <p class="mt-2 text-sm text-slate-500">This therapist profile does not exist or is no longer available.</p>
      <Button class="mt-6 bg-blue-600 text-white hover:bg-blue-700" onclick={() => goto('/book-appointment')}>
        Browse therapists
      </Button>
    </section>
  {:else if loadError}
    <section class="rounded-lg border border-rose-200 bg-rose-50 p-6">
      <h1 class="text-lg font-semibold text-rose-900">Unable to load therapist profile</h1>
      <p class="mt-2 text-sm text-rose-700">{loadError}</p>
    </section>
  {:else if therapist}
    <article class="grid gap-6 lg:grid-cols-[1.15fr_1fr]">
      <section class="space-y-6 rounded-lg border border-blue-100 bg-linear-to-br from-white to-blue-50 p-6 shadow-sm">
        <header class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wide text-blue-500">Therapist profile</p>
            <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">{therapist.name}</h1>
            <p class="text-sm text-blue-700">
              {formatExperience(therapist.years_of_experience)} · {formattedFee}
            </p>
          </div>
          <span
            class={`rounded-full px-3 py-1 text-xs font-semibold ${
              therapist.is_available
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-slate-200 text-slate-600'
            }`}
          >
            {therapist.is_available ? 'Accepting new clients' : 'Unavailable'}
          </span>
        </header>

        <p class="max-w-2xl text-sm leading-relaxed text-slate-700">
          {therapist.bio || 'Bio will be added soon.'}
        </p>

        <div class="grid gap-4 sm:grid-cols-2">
          <section class="rounded-lg border border-blue-100 bg-white p-4">
            <h2 class="text-xs font-semibold uppercase tracking-wide text-blue-500">Specialties</h2>
            <ul class="mt-3 flex flex-wrap gap-2">
              {#if therapist.specialties.length > 0}
                {#each therapist.specialties as specialty (specialty.id)}
                  <li class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                    {specialty.name}
                  </li>
                {/each}
              {:else}
                <li class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
                  Specialty pending
                </li>
              {/if}
            </ul>
          </section>

          <section class="rounded-lg border border-blue-100 bg-white p-4">
            <h2 class="text-xs font-semibold uppercase tracking-wide text-blue-500">Credentials</h2>
            <p class="mt-3 text-sm font-medium text-slate-700">
              {therapist.license_number ? `License ${therapist.license_number}` : 'License on file'}
            </p>
          </section>
        </div>
      </section>

      <section class="space-y-4 rounded-lg border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg font-semibold text-blue-900">Book your session</h2>
          {#if isAvailabilityLoading}
            <span class="text-xs font-medium text-blue-500">Loading times...</span>
          {/if}
        </div>

        <TherapistCalendar bind:selectedDate bind:selectedSlot={selectedSlotId} {availability} />

        <div class="space-y-3 rounded-lg border border-blue-100 bg-blue-50/50 p-4">
          <label class="block space-y-1">
            <span class="text-sm font-medium text-blue-900">Session type</span>
            <select
              class="w-full rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-blue-500"
              bind:value={selectedType}
              disabled={bookingSuccess}
            >
              <option value="video">Video call</option>
              <option value="in_person">In person</option>
              <option value="phone">Phone call</option>
            </select>
          </label>

          <label class="block space-y-1">
            <span class="text-sm font-medium text-blue-900">What would you like to focus on?</span>
            <textarea
              bind:value={reason}
              rows="3"
              class="w-full rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-blue-500 disabled:opacity-60"
              placeholder="Optional context for your therapist"
              disabled={bookingSuccess}
            ></textarea>
          </label>

          <div class="rounded-lg border border-dashed border-blue-200 bg-white p-3 text-sm text-slate-700" aria-live="polite">
            <p><span class="font-medium text-blue-900">Date:</span> {selectedDateLabel}</p>
            <p>
              <span class="font-medium text-blue-900">Time:</span>
              {selectedSlot ? `${selectedSlot.time} (${selectedSlot.duration_minutes} min)` : 'Choose an available slot'}
            </p>
            <p><span class="font-medium text-blue-900">Type:</span> {selectedType.replace('_', ' ')}</p>
          </div>

          {#if bookingError}
            <p class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700" role="alert">
              {bookingError}
            </p>
          {/if}

          {#if bookingSuccess}
            <p class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700" role="status">
              Session booked successfully. Redirecting to your appointments...
            </p>
          {/if}

          <Button
            class="w-full bg-blue-600 text-white hover:bg-blue-700"
            disabled={!canBook || isSubmitting || bookingSuccess}
            onclick={bookSession}
          >
            {#if isSubmitting}
              Saving your booking...
            {:else if bookingSuccess}
              Booked
            {:else if canBook}
              Confirm session
            {:else if !therapist.is_available}
              Therapist unavailable
            {:else}
              Select a date and time
            {/if}
          </Button>
        </div>
      </section>
    </article>
  {/if}
</section>
