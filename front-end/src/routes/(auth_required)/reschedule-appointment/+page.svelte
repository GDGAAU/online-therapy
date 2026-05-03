<script lang="ts">
  import { goto } from '$app/navigation';
  import { Button } from '$lib/components/ui/button';
</script>

<svelte:head>
  <title>Reschedule Appointment - Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-xl p-6">
  <div class="rounded-lg border border-blue-100 bg-white p-6 text-center shadow-sm">
    <h1 class="text-xl font-semibold text-blue-950">Choose an appointment to reschedule</h1>
    <p class="mt-2 text-sm text-slate-600">
      Rescheduling starts from an existing appointment so the correct therapist and availability can be loaded.
    </p>
    <Button class="mt-5 bg-blue-600 text-white hover:bg-blue-700" onclick={() => goto('/appointment')}>
      Back to appointments
    </Button>
  </div>
</section>
