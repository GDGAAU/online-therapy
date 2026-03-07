<script lang="ts">
  /**
   * /appointment — My Appointments page
   *
   * Refactored from the original hardcoded version to use:
   * - Real API data via therapyApi
   * - Proper TypeScript types
   * - Shadcn-style UI components via bits-ui
   * - Sonner toasts for feedback
   */
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import { Search, Bell, Menu, ArrowLeft, Clock, Plus, Loader2 } from 'lucide-svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Badge } from '$lib/components/ui/badge';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { therapyApi, ApiError } from '$lib/api';
  import type { Appointment, AppointmentStatus } from '$lib/types';

  // ─── State ───────────────────────────────────────────────

  let appointments: Appointment[] = [];
  let isLoading = true;
  let searchQuery = '';
  let activeFilter: AppointmentStatus | 'all' = 'all';

  const filters: { label: string; value: AppointmentStatus | 'all' }[] = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Confirmed', value: 'confirmed' },
    { label: 'Completed', value: 'completed' },
    { label: 'Cancelled', value: 'cancelled' }
  ];

  // Cancel modal
  let cancelTarget: Appointment | null = null;
  let isCancelling = false;

  // ─── Derived ─────────────────────────────────────────────

  $: filtered = appointments
    .filter((a) => activeFilter === 'all' || a.status === activeFilter)
    .filter((a) => {
      const q = searchQuery.toLowerCase();
      return (
        a.therapist_name.toLowerCase().includes(q) ||
        a.therapist_specialty.some((s) => s.toLowerCase().includes(q)) ||
        a.status.includes(q)
      );
    });

  // ─── Lifecycle ────────────────────────────────────────────

  onMount(async () => {
    try {
      const res = await therapyApi.listAppointments();
      appointments = res.results;
    } catch (err) {
      toast.error('Failed to load appointments. Please refresh.');
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
        a.id === cancelTarget!.id ? { ...a, status: 'cancelled' as AppointmentStatus } : a
      );
      toast.success('Appointment cancelled.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to cancel appointment.');
    } finally {
      isCancelling = false;
      cancelTarget = null;
    }
  }

  // ─── Helpers ─────────────────────────────────────────────

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }

  const STATUS_COLORS: Record<AppointmentStatus, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    confirmed: 'bg-green-100 text-green-700',
    completed: 'bg-blue-100 text-blue-700',
    cancelled: 'bg-red-100 text-red-700',
    no_show: 'bg-gray-100 text-gray-600'
  };

  function canCancel(a: Appointment) {
    return a.status === 'pending' || a.status === 'confirmed';
  }
</script>

<svelte:head>
  <title>My Appointments — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
    <button on:click={() => goto('/dashboard')} aria-label="Back">
      <ArrowLeft class="text-gray-600" size={22} />
    </button>
    <h1 class="text-lg font-bold text-blue-600">My Appointments</h1>
    <button aria-label="Notifications">
      <Bell class="text-gray-600" size={22} />
    </button>
  </header>

  <main class="max-w-lg mx-auto p-4 space-y-4 pb-24">
    <!-- Search -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
      <Input
        type="text"
        placeholder="Search appointments…"
        bind:value={searchQuery}
        className="pl-10"
      />
    </div>

    <!-- Filters -->
    <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
      {#each filters as f}
        <Button
          on:click={() => (activeFilter = f.value)}
          size="sm"
          variant={activeFilter === f.value ? 'default' : 'outline'}
          className="rounded-full"
        >
          {f.label}
        </Button>
      {/each}
    </div>

    <!-- Loading -->
    {#if isLoading}
      <div class="flex justify-center py-16">
        <Loader2 class="animate-spin text-blue-400" size={32} />
      </div>

    <!-- Empty -->
    {:else if filtered.length === 0}
      <div class="flex flex-col items-center justify-center py-16 text-center space-y-4">
        <div class="text-5xl">🗓️</div>
        <p class="text-gray-500">
          {searchQuery || activeFilter !== 'all'
            ? 'No appointments match your filters.'
            : "You don't have any appointments yet."}
        </p>
        {#if !searchQuery && activeFilter === 'all'}
          <Button
            on:click={() => goto('/book-appointment')}
            className="rounded-xl"
          >
            Book your first appointment
          </Button>
        {/if}
      </div>

    <!-- Appointment Cards -->
    {:else}
      <div class="space-y-3">
        {#each filtered as appt (appt.id)}
          <Card>
            <CardContent className="space-y-3">
            <!-- Top Row -->
            <div class="flex justify-between items-start">
              <div>
                <p class="font-semibold text-gray-900">{appt.therapist_name}</p>
                <p class="text-sm text-gray-500">{appt.therapist_specialty.join(', ') || 'General'}</p>
              </div>
              <Badge className={STATUS_COLORS[appt.status]}>{appt.status}</Badge>
            </div>

            <!-- Time -->
            <div class="flex items-center gap-2 text-gray-500 text-sm">
              <Clock size={14} />
              {formatDate(appt.scheduled_at)}
              ({appt.duration_minutes}min, {appt.appointment_type})
            </div>

            <!-- Actions -->
            {#if appt.status === 'completed'}
              <Button variant="outline" className="w-full">
                View Medical Record
              </Button>
            {:else if canCancel(appt)}
              <div class="flex gap-2">
                <Button className="flex-1">
                  Reschedule
                </Button>
                <Button
                  on:click={() => (cancelTarget = appt)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            {:else if appt.status === 'cancelled'}
              <Button
                on:click={() => goto('/book-appointment')}
                className="w-full"
              >
                Book Again
              </Button>
            {/if}
            </CardContent>
          </Card>
        {/each}
      </div>
    {/if}
  </main>

  <!-- FAB -->
  <div class="fixed bottom-6 right-6">
    <Button
      on:click={() => goto('/book-appointment')}
      className="rounded-full px-5 py-3 shadow-lg"
    >
      <Plus size={18} />
      Book Now
    </Button>
  </div>
</div>

<!-- Cancel Confirmation Modal -->
{#if cancelTarget}
  <div
    class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4"
    role="dialog"
    aria-modal="true"
  >
    <Card className="w-full max-w-sm">
      <CardContent className="space-y-4">
      <h3 class="font-bold text-gray-900 text-lg">Cancel Appointment</h3>
      <p class="text-gray-600 text-sm">
        Are you sure you want to cancel your appointment with
        <strong>{cancelTarget.therapist_name}</strong> on
        <strong>{formatDate(cancelTarget.scheduled_at)}</strong>?
      </p>
      <div class="flex gap-3">
        <Button
          on:click={() => (cancelTarget = null)}
          variant="outline"
          className="flex-1"
        >
          Keep it
        </Button>
        <Button
          on:click={cancelAppointment}
          disabled={isCancelling}
          variant="destructive"
          className="flex-1"
        >
          {#if isCancelling}<Loader2 size={16} class="animate-spin" />{/if}
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
