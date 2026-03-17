<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { Calendar, Clock } from 'lucide-svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { faAngleLeft } from "@fortawesome/free-solid-svg-icons";
  import { FontAwesomeIcon } from "@fortawesome/svelte-fontawesome";
  import type { Appointment, Therapist } from '$lib/types';
  import { therapyApi } from '$lib/api';

  let therapist: Therapist | null = null;
  let appointment: Appointment | null = null;

  let selectedDate = '';
  let selectedTime = '';

  let timeSlots: { time: string; available: boolean }[] = [];

  onMount(async () => {
    try {
      // TODO: Replace with actual appointment ID / therapist fetch logic
      // Example:
      // appointment = await therapyApi.getAppointment(appointmentId);
      // therapist = await therapyApi.getTherapist(appointment.therapist_id);

      // Generate timeSlots dynamically based on fetched appointment data
      timeSlots = [
        { time: "09:00 AM", available: false },
        { time: "09:30 AM", available: false },
        { time: "10:00 AM", available: false },
        { time: "10:30 AM", available: false },
        { time: "11:00 AM", available: true },
        { time: "11:30 AM", available: true },
        { time: "12:00 PM", available: true },
        { time: "12:30 PM", available: true },
        { time: "02:00 PM", available: false },
        { time: "02:30 PM", available: false },
        { time: "03:00 PM", available: true },
        { time: "03:30 PM", available: true }
      ];
    } catch (err) {
      console.error('Failed to load appointment or therapist data', err);
    }
  });

  function goBack() {
    goto('/appointment');
  }

  function handleReschedule() {
    if (!selectedDate || !selectedTime) return;
    // TODO: call API to reschedule appointment
    console.log('Rescheduling with:', { selectedDate, selectedTime });
    goto('/appointment');
  }

  function handleCancel() {
    // TODO: call API to cancel appointment if needed
    goto('/appointment');
  }
</script>

<svelte:head>
  <title>Reschedule Appointment</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="px-4 py-3 flex items-center sticky top-0 z-10">
    <FontAwesomeIcon 
      icon={faAngleLeft} 
      class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" 
      on:click={goBack}
    />
    <h1 class="flex-1 text-center text-lg font-bold text-[#3870FF]">Reschedule Appointment</h1>
    <div class="w-6"></div> 
  </header>

  <main class="w-full max-w-lg lg:max-w-3xl xl:max-w-4xl mx-auto p-4 space-y-6 pb-10">
    
    {#if therapist && appointment}
      <!-- Current Appointment Details -->
      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-gray-800">Current Appointment Details</h2>
        <div class="rounded-xl p-5 space-y-3">
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">Doctor:</span>
            <span class="font-medium text-black">{therapist.name}</span>
          </div>
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">Specialty:</span>
            <span class="font-medium text-black">{therapist.specialty}</span>
          </div>
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">Date & Time:</span>
            <span class="font-medium text-black">
              {appointment.scheduled_at ? new Date(appointment.scheduled_at).toLocaleString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      <!-- Change Date -->
      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-gray-800">Change Date</h2>
        <Input
          type="date"
          bind:value={selectedDate}
          class="w-full h-12 px-4 rounded-xl border-2 border-[#809CFF] bg-white focus:ring-2 focus:ring-[#809CFF]/20 transition-all"
        />
      </div>

      <!-- Change Time -->
      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-gray-800">Change Time</h2>
        <div class="grid grid-cols-2 gap-3">
          {#each timeSlots as slot}
            <button
              on:click={() => slot.available && (selectedTime = slot.time)}
              disabled={!slot.available}
              class={`py-3 px-2 rounded-xl text-sm font-medium transition-all w-full
                ${slot.available 
                  ? selectedTime === slot.time
                    ? 'bg-[#809CFF] text-white'  
                    : 'bg-[#ECF1FF] text-[#3870FF] hover:bg-[#809CFF]/20'  
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {slot.time}
            </button>
          {/each}
        </div>
      </div>

      <!-- Summary -->
      <div class="space-y-3">
        <h2 class="text-lg font-semibold text-gray-800">Summary of New Appointment Details</h2>
        <div class="rounded-xl p-5 space-y-3">
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">Doctor:</span>
            <span class="font-medium text-black">{therapist.name}</span>
          </div>
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">Specialty:</span>
            <span class="font-medium text-black">{therapist.specialty}</span>
          </div>
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">New Date:</span>
            <span class="font-medium text-black">{selectedDate || 'Not selected'}</span>
          </div>
          <div class="flex gap-4 items-center">
            <span class="text-sm text-black">New Time:</span>
            <span class="font-medium text-black">{selectedTime || 'Not selected'}</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-4 pt-4">
        <button
          on:click={handleReschedule}
          disabled={!selectedDate || !selectedTime}
          class="flex-1 py-3 rounded-xl bg-gradient-to-r from-[#38B7FF] to-[#3870FF] text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Reschedule Appointment
        </button>
        <button
          on:click={handleCancel}
          class="flex-1 py-3 rounded-xl border-2 border-[#656565]/30 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    {:else}
      <p class="text-center py-16 text-gray-500">Loading appointment details…</p>
    {/if}
  </main>
</div>