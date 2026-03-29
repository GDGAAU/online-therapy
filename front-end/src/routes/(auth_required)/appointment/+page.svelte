<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import Icon from '$lib/components/icons/Icon.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { therapyApi, ApiError } from '$lib/api';
  import type { Appointment, AppointmentStatus } from '$lib/types';
  import { SearchInput } from '$lib/components/ui/search-input';

  // ─── State────────────────────────────────────

  let appointments = $state<Appointment[]>([]);
  let isLoading = $state(true);
  let searchQuery = $state('');
  let activeFilter = $state<AppointmentStatus | 'all'>('all');

  let cancelTarget = $state<Appointment | null>(null);
  let isCancelling = $state(false);

  const filters: { label: string; value: AppointmentStatus | 'all' }[] = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Confirmed', value: 'confirmed' },
    { label: 'Completed', value: 'completed' },
    { label: 'Cancelled', value: 'cancelled' }
  ];

  // ─── Derived (Svelte 5) ──────────────────────────────────

  let filtered = $derived(
    appointments
      .filter((a) => activeFilter === 'all' || a.status === activeFilter)
      .filter((a) => {
        const q = searchQuery.toLowerCase();
        return (
          a.therapist_name.toLowerCase().includes(q) ||
          a.therapist_specialty.some((s) => s.toLowerCase().includes(q)) ||
          a.status.includes(q)
        );
      })
  );

  // ─── Lifecycle ───────────────────────────────────────────

  onMount(async () => {
    try {
      const res = await therapyApi.listAppointments(
        activeFilter !== 'all' ? activeFilter : undefined
      );
      appointments = res.results;
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? err.message
          : 'Failed to load appointments. Please refresh.'
      );
    } finally {
      isLoading = false;
    }
  });

  // ─── Actions ─────────────────────────────────────────────

  async function cancelAppointment() {
    if (!cancelTarget) return;

    isCancelling = true;

    try {
      await therapyApi.cancelAppointment(cancelTarget.id);

      appointments = appointments.map((a) =>
        a.id === cancelTarget?.id
          ? { ...a, status: 'cancelled' as AppointmentStatus }
          : a
      );

      toast.success('Appointment cancelled.');
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? err.message
          : 'Failed to cancel appointment.'
      );
    } finally {
      isCancelling = false;
      cancelTarget = null;
    }
  }

  // ─── Helpers ─────────────────────────────────────────────

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  const STATUS_COLORS: Record<AppointmentStatus, string> = {
    pending: 'bg-[#FBBC04]/25 text-[#FBBC04]',
    confirmed: 'bg-[#34A853]/25 text-[#34A853]',
    completed: 'bg-[#34A853]/25 text-[#34A853]',
    cancelled: 'bg-[#EA4335]/25 text-[#EA4335]',
    no_show: 'bg-[#EA4335]/25 text-[#EA4335]'
  };

  function canCancel(a: Appointment) {
    return a.status === 'pending' || a.status === 'confirmed';
  }
</script>

<svelte:head>
  <title>My Appointments</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="px-4 py-3 flex items-center sticky top-0 z-10">
    <Button onclick={() => goto('/dashboard')} variant="ghost" size="icon" aria-label="Back">
      <Icon name="arrow-left" class="text-gray-600" size={22} />
    </Button>
    <h1 class="flex-1 text-center text-lg font-bold text-[#3870FF]">My Appointments</h1>
    <Button variant="ghost" size="icon" aria-label="Notifications">
      <Icon name="bell" class="text-gray-600" size={22} />
    </Button>
  </header>

  <main class="w-full max-w-lg lg:max-w-3xl xl:max-w-4xl mx-auto p-4 space-y-4 pb-10">
    <div class="relative">
      <SearchInput 
        bind:value={searchQuery}
        placeholder="Search appointments…"
        onSearch={(query) => console.log('Searching:', query)}
      />
    </div>

    <!-- Filters -->
    <div class="flex overflow-x-auto space-x-3 px-4 py-3 scrollbar-hide">
      {#each filters as f}
        <button
          type="button"
          onclick={() => (activeFilter = f.value)}
          aria-pressed={activeFilter === f.value}
          class={`px-4 py-1.5 rounded-full whitespace-nowrap text-sm font-semibold transition-all duration-200 ${
            activeFilter === f.value
              ? 'bg-[#809CFF] text-white'
              : 'bg-transparent border border-[#809CFF] text-[#809CFF]'
          }`}
        >
          {f.label}
        </button>
      {/each}
    </div>

    <!-- Loading -->
    {#if isLoading}
      <div class="flex justify-center py-16">
        <Icon name="spinner" class="animate-spin text-blue-400" size={32} />
      </div>

    <!-- Empty State -->
    {:else if filtered.length === 0}
      <div class="flex flex-col items-center justify-center py-12 text-center px-4 space-y-6">
        <div class="w-48 h-48 rounded-full flex items-center justify-center">
          <span class="text-7xl">📅</span>
        </div>

        <div class="space-y-2">
          <h2 class="text-xl font-semibold text-gray-800">No appointments yet</h2>
          <p class="text-gray-500 max-w-xs">
            Looks like you don't have any appointments scheduled. Ready to book your first session?
          </p>
        </div>

        <button
          type="button"
          onclick={() => goto('/book-appointment')}
          class="px-8 py-3 rounded-xl bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-white font-medium hover:opacity-90 transition-opacity shadow-md"
        >
          Book Your Appointment
        </button>
      </div>

    <!-- Appointment Cards -->
    {:else}
      <div class="space-y-3">
        {#each filtered as appt (appt.id)}
          <div class="bg-[#ECF1FF] border border-[#656565]/30 shadow-md rounded-xl p-6 w-full">
            <div class="flex justify-between items-start mb-3">
              <div>
                <p class="font-medium text-black">{appt.therapist_name}</p>
                <p class="text-sm text-black/60">{appt.therapist_specialty.join(', ') || 'General'}</p>
              </div>
              <div class={STATUS_COLORS[appt.status] + " px-3 py-1 text-sm font-medium rounded-md"}>
                {appt.status}
              </div>
            </div>

            <div class="flex items-center gap-2 text-black/40 text-sm mb-4">
              <Icon name="clock" class="text-black/40" size={14} />
              {formatDate(appt.scheduled_at)}
              ({appt.duration_minutes}min, {appt.appointment_type})
            </div>

            {#if appt.status === 'completed'}
              <Button class="w-full bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-white hover:opacity-90 transition-opacity rounded-xl">
                View Medical Record
              </Button>

            {:else if canCancel(appt)}
              <div class="flex gap-2">
                <Button
                  onclick={() => goto(`/reschedule-appointment/${appt.id}`)}
                  class="flex-1 bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-white hover:opacity-90 transition-opacity rounded-xl"
                >
                  Reschedule
                </Button>

                <Button
                  onclick={() => (cancelTarget = appt)}
                  class="flex-1 bg-transparent border-2 border-transparent bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-transparent hover:opacity-90 transition-opacity rounded-xl py-2 px-4 font-medium"
                  style="background-image: linear-gradient(to right, #38B7FF, #3870FF); -webkit-background-clip: text; background-clip: text; border-image: linear-gradient(to right, #38B7FF, #3870FF) 1; border-image-slice: 1; border-radius: 0.75rem;"
                >
                  Cancel
                </Button>
              </div>

            {:else if appt.status === 'cancelled'}
              <Button
                onclick={() => goto('/book-appointment')}
                class="w-full bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-white hover:opacity-90 transition-opacity rounded-xl"
              >
                Book Again
              </Button>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </main>

  <!-- FAB -->
  <div class="fixed bottom-6 right-6">
    <Button
      onclick={() => goto('/book-appointment')}
  class="rounded-full px-5 py-3 lg:px-8 lg:py-4 lg:text-lg shadow-lg bg-linear-to-r from-[#38B7FF] to-[#3870FF] text-white hover:opacity-90 transition-opacity"
    >
  <Icon name="plus" class="mr-1" size={18} />
      Book Now
    </Button>
  </div>
</div>

<!-- Cancel Modal -->
{#if cancelTarget}
  <div class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4">
    <Card className="w-full max-w-sm">
      <CardContent className="space-y-4">
        <h3 class="font-bold text-gray-900 text-lg">Cancel Appointment</h3>
        <p class="text-gray-600 text-sm">
          Are you sure you want to cancel your appointment with
          <strong>{cancelTarget.therapist_name}</strong> on
          <strong>{formatDate(cancelTarget.scheduled_at)}</strong>?
        </p>
        <div class="flex gap-3">
          <Button onclick={() => (cancelTarget = null)} variant="outline" className="flex-1">
            Keep it
          </Button>
          <Button onclick={cancelAppointment} disabled={isCancelling} variant="destructive" className="flex-1">
            {#if isCancelling}
              <Icon name="spinner" class="animate-spin" size={16} />
            {/if}
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
{/if}

<style>
  .scrollbar-hide::-webkit-scrollbar { display: none; }
  .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
