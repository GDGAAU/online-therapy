<script lang="ts">
  /**
   * /book-appointment — Book an Appointment page
   * Fetches real therapists from the API.
   */
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import { Search, ArrowLeft, Bell, UserCircle, Loader2 } from 'lucide-svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import { therapyApi, ApiError } from '$lib/api';
  import { bookAppointmentSchema } from '$lib/schemas';
  import type { Therapist } from '$lib/types';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Badge } from '$lib/components/ui/badge';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { Select } from '$lib/components/ui/select';
  import { Textarea } from '$lib/components/ui/textarea';

  // ─── State ───────────────────────────────────────────────

  let therapists: Therapist[] = $state([]);
  let isLoading = $state(true);
  let searchQuery = $state('');
  let activeSpecialty = $state('all');
  let selectedTherapist: Therapist | null = $state(null);
  let showBookingModal = $state(false);

  const specialties = ['all', 'Pediatric', 'General Medicine', 'Psychiatry', 'Psychotherapy'];

  let filteredTherapists = $derived(therapists
    .filter((t) =>
      activeSpecialty === 'all' ||
      t.specialties.some((s) => s.name === activeSpecialty)
    )
    .filter((t) => t.name.toLowerCase().includes(searchQuery.toLowerCase())));

  // ─── Booking Form ─────────────────────────────────────────

  const { form, errors, enhance, submitting } = superForm(
    {
      therapist_id: '',
      scheduled_at: '',
      appointment_type: 'video' as const,
      reason: ''
    },
    {
      validators: zod(bookAppointmentSchema as any),
      SPA: true,
      async onUpdate({ form }) {
        if (!form.valid) return;
        try {
          await therapyApi.createAppointment({
            therapist_id: form.data.therapist_id,
            scheduled_at: new Date(form.data.scheduled_at).toISOString(),
            appointment_type: form.data.appointment_type,
            reason: form.data.reason
          });
          toast.success('Appointment booked successfully!');
          showBookingModal = false;
          goto('/appointment');
        } catch (err) {
          toast.error(err instanceof ApiError ? err.message : 'Failed to book. Please try again.');
        }
      }
    }
  );

  function openBookingModal(therapist: Therapist) {
    selectedTherapist = therapist;
    $form.therapist_id = therapist.id;
    showBookingModal = true;
  }

  // ─── Lifecycle ───────────────────────────────────────────

  onMount(async () => {
    try {
      const res = await therapyApi.listTherapists();
      therapists = res.results;
    } catch {
      toast.error('Failed to load therapists.');
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Book Appointment — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
    <Button on:click={() => goto('/dashboard')} variant="ghost" size="icon" aria-label="Back">
      <ArrowLeft class="text-gray-600" size={22} />
    </Button>
    <h1 class="text-lg font-bold text-blue-600">Book Appointment</h1>
    <Button variant="ghost" size="icon" aria-label="Notifications">
      <Bell class="text-gray-600" size={22} />
    </Button>
  </header>

  <main class="max-w-lg mx-auto p-4 space-y-4 pb-10">
    <!-- Search -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
      <Input
        type="text"
        placeholder="Search therapists…"
        bind:value={searchQuery}
        className="pl-10"
      />
    </div>

    <!-- Specialty Filters -->
    <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
      {#each specialties as s}
        <Button
          on:click={() => (activeSpecialty = s)}
          size="sm"
          variant={activeSpecialty === s ? 'default' : 'outline'}
          className="rounded-full whitespace-nowrap text-sm capitalize"
        >
          {s === 'all' ? 'All' : s}
        </Button>
      {/each}
    </div>

    <!-- Loading -->
    {#if isLoading}
      <div class="flex justify-center py-16">
        <Loader2 class="animate-spin text-blue-400" size={32} />
      </div>

    <!-- Empty -->
    {:else if filteredTherapists.length === 0}
      <div class="text-center py-16 text-gray-500">
        No therapists match your search.
      </div>

    <!-- Therapist Cards -->
    {:else}
      <div class="space-y-3">
        {#each filteredTherapists as therapist (therapist.id)}
          <Card>
            <CardContent className="space-y-3">
              <div class="flex items-start gap-3">
                <!-- Avatar -->
                {#if therapist.avatar_url}
                  <img src={therapist.avatar_url} alt={therapist.name} class="w-12 h-12 rounded-full object-cover" />
                {:else}
                  <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <UserCircle class="text-blue-400" size={28} />
                  </div>
                {/if}

                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <p class="font-semibold text-gray-900">{therapist.name}</p>
                      <p class="text-sm text-gray-500">
                        {therapist.specialties.map((s) => s.name).join(', ') || 'General'}
                      </p>
                      <p class="text-xs text-gray-400">{therapist.years_of_experience} years experience</p>
                    </div>
                    <Badge variant={therapist.is_available ? 'success' : 'destructive'}>
                      {therapist.is_available ? 'Available' : 'Unavailable'}
                    </Badge>
                  </div>
                </div>
              </div>

              <Button
                on:click={() => openBookingModal(therapist)}
                disabled={!therapist.is_available}
                className="w-full"
                variant={therapist.is_available ? 'default' : 'secondary'}
              >
                {therapist.is_available ? 'Book Appointment' : 'Unavailable'}
              </Button>
            </CardContent>
          </Card>
        {/each}
      </div>
    {/if}
  </main>
</div>

<!-- Booking Modal -->
{#if showBookingModal && selectedTherapist}
  <div
    class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4"
    role="dialog"
    aria-modal="true"
  >
    <Card className="w-full max-w-sm">
      <CardContent className="space-y-4">
        <h3 class="font-bold text-gray-900 text-lg">Book with {selectedTherapist.name}</h3>

      <form use:enhance method="POST" class="space-y-4">
        <!-- Date & Time -->
        <div class="space-y-1">
          <Label forValue="scheduled_at">Date & Time</Label>
          <Input
            id="scheduled_at"
            type="datetime-local"
            bind:value={$form.scheduled_at}
          />
          {#if $errors.scheduled_at}
            <p class="text-red-500 text-xs">{$errors.scheduled_at}</p>
          {/if}
        </div>

        <!-- Type -->
        <div class="space-y-1">
          <Label forValue="appointment_type">Session Type</Label>
          <Select
            id="appointment_type"
            bind:value={$form.appointment_type}
          >
            <option value="video">Video Call</option>
            <option value="phone">Phone Call</option>
            <option value="in_person">In Person</option>
          </Select>
        </div>

        <!-- Reason -->
        <div class="space-y-1">
          <Label forValue="reason">Reason (optional)</Label>
          <Textarea
            id="reason"
            rows="2"
            bind:value={$form.reason}
            placeholder="Briefly describe what you'd like to discuss…"
            className="resize-none"
          />
        </div>

        <div class="flex gap-3">
          <Button
            type="button"
            on:click={() => (showBookingModal = false)}
            className="flex-1"
            variant="outline"
          >
            Cancel
          </Button>
          <Button type="submit" disabled={$submitting} className="flex-1">
            {#if $submitting}<Loader2 size={16} class="animate-spin" />{/if}
            Confirm
          </Button>
        </div>
      </form>
      </CardContent>
    </Card>
  </div>
{/if}
