<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { ApiError, therapyApi } from '$lib/api';
  import { Button } from '$lib/components/ui/button';
  import TherapistCalendar, { type TimeSlot } from '$lib/components/booking/TherapistCalendar.svelte';
  import type { Appointment, AppointmentType, Therapist } from '$lib/types';
  import {
    adaptAvailability,
    formatDateKey,
    formatDateTime,
    formatFee,
    formatSessionType
  } from '$lib/utils/therapy';

  const availabilityWindowDays = 35;

  let appointment = $state<Appointment | null>(null);
  let therapist = $state<Therapist | null>(null);
  let availability = $state<Record<string, TimeSlot[]>>({});
  let selectedDate = $state('');
  let selectedSlotId = $state('');
  let selectedType = $state<AppointmentType>('video');
  let isLoading = $state(true);
  let isSubmitting = $state(false);
  let loadError = $state('');
  let submitError = $state('');
  let redirectTimer: ReturnType<typeof setTimeout> | null = null;

  let selectedSlot = $derived(
    selectedDate
      ? (availability[selectedDate] ?? []).find((slot) => slot.id === selectedSlotId) ?? null
      : null
  );

  let canSubmit = $derived(Boolean(appointment && selectedSlot));

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

  onMount(async () => {
    const appointmentId = $page.params.id;

    if (!appointmentId) {
      loadError = 'Appointment ID is required.';
      isLoading = false;
      return;
    }

    try {
      const appointmentResponse = await therapyApi.getAppointment(appointmentId);
      appointment = appointmentResponse;
      selectedType = appointmentResponse.appointment_type;

      const therapistResponse = await therapyApi.getTherapist(appointmentResponse.therapist);
      therapist = therapistResponse;
      await loadAvailability(therapistResponse.id);
    } catch (err) {
      loadError = err instanceof ApiError ? err.message : 'Failed to load appointment details.';
    } finally {
      isLoading = false;
    }
  });

  onDestroy(() => {
    if (redirectTimer) clearTimeout(redirectTimer);
  });

  async function handleReschedule() {
    if (!appointment || !selectedSlot) return;

    isSubmitting = true;
    submitError = '';

    try {
      await therapyApi.rescheduleAppointment(appointment.id, {
        scheduled_at: new Date(selectedSlot.startAt).toISOString(),
        appointment_type: selectedType
      });

      toast.success('Appointment rescheduled.');
      redirectTimer = setTimeout(() => {
        goto('/appointment');
      }, 800);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        submitError = 'That time was just booked. Choose another available slot.';
        if (therapist) await loadAvailability(therapist.id);
      } else {
        submitError = err instanceof ApiError ? err.message : 'Failed to reschedule appointment.';
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Reschedule Appointment - Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-5xl space-y-6 p-4 pb-12 sm:p-6 lg:p-8">
  <div class="flex items-center justify-between">
    <Button variant="outline" class="border-blue-200 text-blue-700 hover:bg-blue-50" onclick={() => goto('/appointment')}>
      Back to appointments
    </Button>
  </div>

  {#if isLoading}
    <div class="grid gap-6 lg:grid-cols-[1fr_1.2fr]" aria-live="polite">
      <article class="h-48 animate-pulse rounded-lg border border-blue-100 bg-white p-6 shadow-sm"></article>
      <article class="h-96 animate-pulse rounded-lg border border-blue-100 bg-white p-6 shadow-sm"></article>
    </div>
  {:else if loadError}
    <section class="rounded-lg border border-rose-200 bg-rose-50 p-6">
      <h1 class="text-lg font-semibold text-rose-900">Unable to load appointment</h1>
      <p class="mt-2 text-sm text-rose-700">{loadError}</p>
    </section>
  {:else if appointment && therapist}
    <div class="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
      <section class="space-y-4 rounded-lg border border-blue-100 bg-white p-5 shadow-sm">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-blue-500">Current Appointment</p>
          <h1 class="mt-2 text-2xl font-semibold text-blue-950">{therapist.name}</h1>
          <p class="mt-1 text-sm text-slate-600">{therapist.specialties.map((s) => s.name).join(', ') || 'General therapy'}</p>
        </div>

        <dl class="space-y-3 text-sm">
          <div class="rounded-lg bg-blue-50 p-3">
            <dt class="font-medium text-blue-900">Current time</dt>
            <dd class="mt-1 text-slate-700">{formatDateTime(appointment.scheduled_at)}</dd>
          </div>
          <div class="rounded-lg bg-blue-50 p-3">
            <dt class="font-medium text-blue-900">Session type</dt>
            <dd class="mt-1 capitalize text-slate-700">{formatSessionType(appointment.appointment_type)}</dd>
          </div>
          <div class="rounded-lg bg-blue-50 p-3">
            <dt class="font-medium text-blue-900">Consultation fee</dt>
            <dd class="mt-1 text-slate-700">{formatFee(therapist.consultation_fee)}</dd>
          </div>
        </dl>

        <label class="block space-y-1 text-sm">
          <span class="font-medium text-blue-900">New session type</span>
          <select
            bind:value={selectedType}
            class="h-11 w-full rounded-lg border border-blue-200 bg-white px-3 text-sm outline-none focus:border-blue-500"
          >
            <option value="video">Video call</option>
            <option value="in_person">In person</option>
            <option value="phone">Phone call</option>
          </select>
        </label>
      </section>

      <section class="space-y-4 rounded-lg border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
        <h2 class="text-lg font-semibold text-blue-900">Choose a new time</h2>
        <TherapistCalendar bind:selectedDate bind:selectedSlot={selectedSlotId} {availability} />

        <div class="rounded-lg border border-dashed border-blue-200 bg-blue-50/50 p-3 text-sm text-slate-700" aria-live="polite">
          <p>
            <span class="font-medium text-blue-900">New time:</span>
            {selectedSlot ? `${selectedDate} at ${selectedSlot.time}` : 'Choose an available slot'}
          </p>
          <p><span class="font-medium text-blue-900">Type:</span> {formatSessionType(selectedType)}</p>
        </div>

        {#if submitError}
          <p class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700" role="alert">
            {submitError}
          </p>
        {/if}

        <div class="flex flex-col gap-3 sm:flex-row">
          <Button
            class="flex-1 bg-blue-600 text-white hover:bg-blue-700"
            disabled={!canSubmit || isSubmitting}
            onclick={handleReschedule}
          >
            {isSubmitting ? 'Rescheduling...' : 'Reschedule appointment'}
          </Button>
          <Button variant="outline" class="flex-1 border-slate-200" onclick={() => goto('/appointment')}>
            Cancel
          </Button>
        </div>
      </section>
    </div>
  {/if}
</section>
