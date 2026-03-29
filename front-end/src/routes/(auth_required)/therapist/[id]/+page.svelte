<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Button } from '$lib/components/ui/button';
  import TherapistCalendar from '$lib/components/booking/TherapistCalendar.svelte';
  import {
    buildMockAvailability,
    defaultMockTherapistId,
    mockTherapistsById,
    type MockAvailabilitySlot,
    type MockTherapistDetail
  } from '$lib/mock/therapist-booking';
  import type { AppointmentType } from '$lib/types';

  let isLoading = $state(true);
  let isSubmitting = $state(false);
  let bookingSuccess = $state(false);

  let therapist = $state<MockTherapistDetail | null>(null);
  let availability = $state<Record<string, MockAvailabilitySlot[]>>({});

  let selectedDate = $state('');
  let selectedSlotId = $state('');
  let selectedType = $state<AppointmentType>('video');
  let reason = $state('');

  let payloadPreview = $derived(
    therapist && selectedDate && selectedSlotId
      ? {
          therapist_id: therapist.id,
          scheduled_at:
            (availability[selectedDate] ?? []).find((slot) => slot.id === selectedSlotId)?.startAt ?? '',
          appointment_type: selectedType,
          reason: reason.trim()
        }
      : null
  );

  let selectedSlot = $derived(
    selectedDate
      ? (availability[selectedDate] ?? []).find((slot) => slot.id === selectedSlotId) ?? null
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

  let canBook = $derived(Boolean(payloadPreview?.scheduled_at));

  let formattedFee = $derived(
    therapist?.consultation_fee ? `$${therapist.consultation_fee}/session` : 'Fee shared after consultation'
  );

  onMount(async () => {
    await new Promise((resolve) => setTimeout(resolve, 550));

    const routeTherapistId = $page.params.id || defaultMockTherapistId;
    therapist = mockTherapistsById[routeTherapistId] ?? mockTherapistsById[defaultMockTherapistId];

    availability = buildMockAvailability(new Date(), 35);
    isLoading = false;
  });

  async function bookSession() {
    if (!canBook || !payloadPreview) return;

    isSubmitting = true;
    bookingSuccess = false;

    await new Promise((resolve) => setTimeout(resolve, 700));

    bookingSuccess = true;
    isSubmitting = false;
  }
</script>

<svelte:head>
  <title>Therapist Profile & Booking</title>
</svelte:head>

<section class="mx-auto max-w-6xl space-y-6 p-4 pb-12 sm:p-6 lg:p-8">
  <div class="flex items-center justify-between">
    <Button
      variant="outline"
      class="border-blue-200 text-blue-700 hover:bg-blue-50"
      onclick={() => goto('/book-appointment')}
    >
      ← Back to therapists
    </Button>
  </div>

  {#if isLoading}
    <article class="grid gap-6 lg:grid-cols-[1.15fr_1fr]" aria-live="polite">
      <div class="animate-pulse space-y-4 rounded-2xl border border-blue-100 bg-white p-6">
        <div class="h-6 w-52 rounded bg-blue-100"></div>
        <div class="h-4 w-40 rounded bg-blue-50"></div>
        <div class="h-24 rounded-xl bg-blue-50"></div>
      </div>
      <div class="animate-pulse rounded-2xl border border-blue-100 bg-white p-6">
        <div class="h-8 w-44 rounded bg-blue-100"></div>
        <div class="mt-4 h-56 rounded-xl bg-blue-50"></div>
      </div>
    </article>
  {:else if therapist}
    <article class="grid gap-6 lg:grid-cols-[1.15fr_1fr]">
      <section class="space-y-6 rounded-2xl border border-blue-100 bg-linear-to-br from-white to-blue-50 p-6 shadow-sm">
        <header class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Therapist profile</p>
            <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">{therapist.name}</h1>
            <p class="text-sm text-blue-700">
              {therapist.years_of_experience} years experience • {formattedFee}
            </p>
          </div>
          <span
            class={`rounded-full px-3 py-1 text-xs font-semibold ${
              therapist.is_available
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-rose-100 text-rose-700'
            }`}
          >
            {therapist.is_available ? 'Accepting new clients' : 'Waitlist only'}
          </span>
        </header>

        <p class="max-w-2xl text-sm leading-relaxed text-slate-700">{therapist.bio}</p>

        <div class="grid gap-4 sm:grid-cols-2">
          <section class="rounded-xl border border-blue-100 bg-white p-4">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-blue-500">Specialties</h2>
            <ul class="mt-3 flex flex-wrap gap-2">
              {#each therapist.specialties as specialty (specialty.id)}
                <li class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                  {specialty.name}
                </li>
              {/each}
            </ul>
          </section>

          <section class="rounded-xl border border-blue-100 bg-white p-4">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-blue-500">Credentials</h2>
            <p class="mt-3 text-sm font-medium text-slate-700">License {therapist.license_number}</p>
          </section>
        </div>

        <section class="rounded-xl border border-blue-100 bg-white p-4">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-blue-500">How booking maps to backend</h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-700">
            This UI mirrors your API payload for <code class="rounded bg-slate-100 px-1">CreateAppointmentSerializer</code>:
            <code class="rounded bg-slate-100 px-1">therapist_id</code>,
            <code class="rounded bg-slate-100 px-1">scheduled_at</code>,
            <code class="rounded bg-slate-100 px-1">appointment_type</code>, and optional
            <code class="rounded bg-slate-100 px-1">reason</code>.
          </p>
        </section>
      </section>

      <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
        <h2 class="text-lg font-semibold text-blue-900">Book your session</h2>

        <TherapistCalendar bind:selectedDate bind:selectedSlot={selectedSlotId} {availability} />

        <div class="space-y-3 rounded-xl border border-blue-100 bg-blue-50/50 p-4">
          <label class="block space-y-1">
            <span class="text-sm font-medium text-blue-900">Session type</span>
            <select
              class="w-full rounded-xl border border-blue-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-blue-500"
              bind:value={selectedType}
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
              class="w-full rounded-xl border border-blue-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-blue-500"
              placeholder="Optional context for your therapist"
            ></textarea>
          </label>

          <div class="rounded-xl border border-dashed border-blue-200 bg-white p-3 text-sm text-slate-700" aria-live="polite">
            <p><span class="font-medium text-blue-900">Date:</span> {selectedDateLabel}</p>
            <p>
              <span class="font-medium text-blue-900">Time:</span>
              {selectedSlot ? `${selectedSlot.time} (${selectedSlot.duration_minutes} min)` : 'Choose an available slot'}
            </p>
            <p><span class="font-medium text-blue-900">Type:</span> {selectedType.replace('_', ' ')}</p>
          </div>

          <Button
            class="w-full bg-blue-600 text-white hover:bg-blue-700"
            disabled={!canBook || isSubmitting}
            onclick={bookSession}
          >
            {#if isSubmitting}
              Saving your booking…
            {:else if canBook}
              Confirm session
            {:else}
              Select a date and time
            {/if}
          </Button>

          {#if bookingSuccess && payloadPreview}
            <p class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700" role="status">
              Booking mocked successfully 🎉 Payload ready for API: {payloadPreview.scheduled_at}
            </p>
          {/if}
        </div>
      </section>
    </article>
  {/if}
</section>
