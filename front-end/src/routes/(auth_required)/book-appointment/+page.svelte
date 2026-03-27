<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import { ArrowLeft, UserCircle, Loader2 } from 'lucide-svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import { therapyApi, ApiError } from '$lib/api';
  import { bookAppointmentSchema } from '$lib/schemas';
  import type { Therapist } from '$lib/types';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { Select } from '$lib/components/ui/select';
  import { Textarea } from '$lib/components/ui/textarea';
  import { SearchInput } from '$lib/components/ui/search-input';

  // ─── State (Svelte 5) ────────────────────────────────────
  let therapists = $state<Therapist[]>([]);
  let isLoading = $state(true);
  let searchQuery = $state('');
  let activeSpecialty = $state('all');
  let selectedTherapist = $state<Therapist | null>(null);
  let showBookingModal = $state(false);

  const specialties = ['all', 'Pediatric', 'General Medicine', 'Psychiatry', 'Psychotherapy'];

  // ─── Derived ─────────────────────────────────────────────
  let filteredTherapists = $derived(
    therapists
      .filter((t) =>
        activeSpecialty === 'all' ||
        t.specialties.some((s) =>
          s.name.toLowerCase() === activeSpecialty.toLowerCase()
        )
      )
      .filter((t) =>
        t.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
  );

  // ─── Form ────────────────────────────────────────────────
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
          toast.error(
            err instanceof ApiError
              ? err.message
              : 'Failed to book. Please try again.'
          );
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
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? err.message
          : 'Failed to load therapists.'
      );
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Book Appointment — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
 <header class="border-gray-100 px-4 py-3 flex items-center sticky top-0 z-10">
  <Button on:click={() => goto('/dashboard')} variant="ghost" size="icon" aria-label="Back">
    <ArrowLeft class="text-gray-600" size={22} />
  </Button>
  <h1 class="flex-1 text-center text-lg font-bold text-[#3870FF]">Book Appointment</h1>
</header>

<main class="w-full max-w-lg lg:max-w-3xl xl:max-w-4xl mx-auto p-4 space-y-4 pb-10">
  <SearchInput 
    bind:value={searchQuery}
    placeholder="Search by doctor or speciality"
    onSearch={(query) => console.log('Searching for:', query)}
  />

  <!-- FILTERS -->
  <div class="flex overflow-x-auto space-x-3 px-4 py-3 scrollbar-hide">
    {#each specialties as s}
      <div
        class={`px-4 py-1.5 rounded-full whitespace-nowrap cursor-pointer text-sm font-semibold transition-all duration-200 ${
          activeSpecialty === s
            ? 'bg-[#809CFF] text-white'  
            : 'bg-[#ECF1FF] border border-[#809CFF] text-[#809CFF]' 
        }`}
        on:click={() => activeSpecialty = s}
      >
        {s === 'all' ? 'All' : s}
      </div>
    {/each}
  </div>

  {#if isLoading}
    <div class="flex justify-center py-16">
      <Loader2 class="animate-spin text-blue-400" size={32} />
    </div>

  {:else if filteredTherapists.length === 0}
    <div class="text-center py-16 text-gray-500">
      No therapists match your search.
    </div>

  {:else}
    <div class="space-y-3">
      {#each filteredTherapists as therapist (therapist.id)}
        <div class="bg-[#ECF1FF] border border-[#656565]/30 shadow-sm rounded-xl p-8 w-full">
          <div class="flex items-start gap-3 mb-8">
            <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center flex-shrink-0">
              <UserCircle class="text-black" size={24} />
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <p class="font-medium text-black truncate">{therapist.name}</p>
                  <p class="text-sm text-black/60 truncate">
                    {therapist.specialties.map((s) => s.name).join(', ') || 'General Medicine'}
                  </p>
                  <p class="text-xs text-black/40 mt-0.5">
                    {therapist.years_of_experience} years experience
                  </p>
                </div>

                {#if therapist.is_available}
                  <div class="bg-[#34A853]/25 text-[#34A853] px-3 py-0.5 text-sm font-medium rounded-md">
                    Available
                  </div>
                {:else}
                  <div class="bg-red-500/25 text-red-600 px-3 py-0.5 text-sm font-medium rounded-md">
                    Unavailable
                  </div>
                {/if}
              </div>
            </div>
          </div>

          <Button
            on:click={() => openBookingModal(therapist)}
            disabled={!therapist.is_available}
            class="w-full bg-gradient-to-r from-[#38B7FF] to-[#3870FF] text-white hover:opacity-90 transition-opacity"
            variant={therapist.is_available ? 'default' : 'secondary'}
          >
            {therapist.is_available ? 'Book Appointment' : 'Unavailable'}
          </Button>
        </div>
      {/each}
    </div>
  {/if}
</main>
</div>

{#if showBookingModal && selectedTherapist}
  <div class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-4">
    <Card className="w-full max-w-sm">
      <CardContent className="space-y-4">
        <h3 class="font-bold text-gray-900 text-lg">
          Book with {selectedTherapist.name}
        </h3>

        <form use:enhance method="POST" class="space-y-4">
          <div class="space-y-1">
            <Label forValue="scheduled_at">Date & Time</Label>
            <Input type="datetime-local" bind:value={$form.scheduled_at} />
            {#if $errors.scheduled_at}
              <p class="text-red-500 text-xs">{$errors.scheduled_at}</p>
            {/if}
          </div>

          <div class="space-y-1">
            <Label forValue="appointment_type">Session Type</Label>
            <Select bind:value={$form.appointment_type}>
              <option value="video">Video Call</option>
              <option value="phone">Phone Call</option>
              <option value="in_person">In Person</option>
            </Select>
          </div>

          <div class="space-y-1">
            <Label forValue="reason">Reason (optional)</Label>
            <Textarea
              rows="2"
              bind:value={$form.reason}
              placeholder="Briefly describe what you'd like to discuss…"
              className="resize-none"
            />
          </div>

          <div class="flex gap-3">
            <Button type="button" on:click={() => (showBookingModal = false)} className="flex-1" variant="outline">
              Cancel
            </Button>
            <Button type="submit" disabled={$submitting} className="flex-1">
              {#if $submitting}
                <Loader2 size={16} class="animate-spin" />
              {/if}
              Confirm
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
{/if}