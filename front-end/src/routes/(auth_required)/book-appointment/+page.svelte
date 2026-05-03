<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import Icon from '$lib/components/icons/Icon.svelte';
  import { superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import { therapyApi, ApiError } from '$lib/api';
  import { bookAppointmentSchema } from '$lib/schemas';
  import type { Specialty, Therapist } from '$lib/types';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { Select } from '$lib/components/ui/select';
  import { Textarea } from '$lib/components/ui/textarea';
  import { SearchInput } from '$lib/components/ui/search-input';

  const allSpecialtiesSlug = 'all';
  const avatarFallbackClasses = [
    'bg-blue-100 text-blue-700',
    'bg-emerald-100 text-emerald-700',
    'bg-cyan-100 text-cyan-700',
    'bg-amber-100 text-amber-800',
    'bg-rose-100 text-rose-700',
    'bg-slate-100 text-slate-700'
  ];

  let therapists = $state<Therapist[]>([]);
  let specialties = $state<Specialty[]>([]);
  let failedAvatarIds = $state<Set<string>>(new Set());
  let isLoading = $state(true);
  let isFiltering = $state(false);
  let searchQuery = $state('');
  let activeSpecialty = $state(allSpecialtiesSlug);
  let selectedTherapist = $state<Therapist | null>(null);
  let showBookingModal = $state(false);
  let therapistRequestId = 0;

  let filteredTherapists = $derived(
    therapists.filter((therapist) => {
      const query = searchQuery.trim().toLowerCase();

      if (!query) return true;

      return (
        therapist.name.toLowerCase().includes(query) ||
        therapist.specialties.some((specialty) => specialty.name.toLowerCase().includes(query))
      );
    })
  );

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

          toast.success('Appointment booked successfully.');
          showBookingModal = false;
          goto('/appointment');
        } catch (err) {
          toast.error(err instanceof ApiError ? err.message : 'Failed to book. Please try again.');
        }
      }
    }
  );

  function getInitials(name: string) {
    const cleanedName = name.replace(/^Dr\.\s*/i, '').trim();
    const parts = cleanedName.split(/\s+/).filter(Boolean);

    if (parts.length === 0) return 'DR';
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();

    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  }

  function getAvatarFallbackClass(therapist: Therapist) {
    const hashKey = therapist.id || therapist.name;
    const hash = hashKey.split('').reduce((total, char) => total + char.charCodeAt(0), 0);
    return avatarFallbackClasses[hash % avatarFallbackClasses.length];
  }

  function markAvatarFailed(therapistId: string) {
    failedAvatarIds = new Set(failedAvatarIds).add(therapistId);
  }

  function formatExperience(years: number) {
    return `${years} ${years === 1 ? 'year' : 'years'} experience`;
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

  async function loadTherapists(specialtySlug = allSpecialtiesSlug) {
    const requestId = ++therapistRequestId;
    isFiltering = true;

    try {
      const response = await therapyApi.listTherapists(
        specialtySlug === allSpecialtiesSlug ? undefined : specialtySlug
      );

      if (requestId === therapistRequestId) {
        therapists = response.results;
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to load therapists.');
    } finally {
      if (requestId === therapistRequestId) {
        isFiltering = false;
      }
    }
  }

  async function selectSpecialty(specialtySlug: string) {
    if (specialtySlug === activeSpecialty && !isLoading) return;

    activeSpecialty = specialtySlug;
    await loadTherapists(specialtySlug);
  }

  function openBookingModal(therapist: Therapist) {
    if (!therapist.is_available) return;

    selectedTherapist = therapist;
    $form.therapist_id = therapist.id;
    showBookingModal = true;
  }

  onMount(async () => {
    try {
      const [therapistResponse, specialtyResponse] = await Promise.all([
        therapyApi.listTherapists(),
        therapyApi.listSpecialties()
      ]);

      therapists = therapistResponse.results;
      specialties = specialtyResponse.results;
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to load therapists.');
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Book Appointment - Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-slate-50">
  <header class="sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center gap-3">
      <Button onclick={() => goto('/dashboard')} variant="ghost" size="icon" aria-label="Back">
        <Icon name="arrow-left" class="text-slate-600" size={22} />
      </Button>
      <div class="min-w-0">
        <h1 class="text-lg font-semibold text-slate-950">Book Appointment</h1>
        <p class="text-sm text-slate-500">Choose a therapist and reserve a session.</p>
      </div>
    </div>
  </header>

  <main class="mx-auto w-full max-w-7xl space-y-5 p-4 pb-10 sm:p-6 lg:p-8">
    <section class="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
      <SearchInput
        bind:value={searchQuery}
        placeholder="Search by therapist or specialty"
        onSearch={(query) => (searchQuery = query)}
      />

      <div class="text-sm font-medium text-slate-500">
        {filteredTherapists.length}
        {filteredTherapists.length === 1 ? 'therapist' : 'therapists'}
      </div>
    </section>

    <section class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide" aria-label="Specialty filters">
      <button
        type="button"
        aria-pressed={activeSpecialty === allSpecialtiesSlug}
        class={`h-9 rounded-full border px-4 text-sm font-semibold transition ${
          activeSpecialty === allSpecialtiesSlug
            ? 'border-blue-600 bg-blue-600 text-white'
            : 'border-slate-200 bg-white text-slate-600 hover:border-blue-200 hover:text-blue-700'
        }`}
        onclick={() => selectSpecialty(allSpecialtiesSlug)}
      >
        All
      </button>

      {#each specialties as specialty (specialty.id)}
        <button
          type="button"
          aria-pressed={activeSpecialty === specialty.slug}
          class={`h-9 rounded-full border px-4 text-sm font-semibold transition ${
            activeSpecialty === specialty.slug
              ? 'border-blue-600 bg-blue-600 text-white'
              : 'border-slate-200 bg-white text-slate-600 hover:border-blue-200 hover:text-blue-700'
          }`}
          onclick={() => selectSpecialty(specialty.slug)}
        >
          {specialty.name}
        </button>
      {/each}
    </section>

    {#if isLoading}
      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" aria-live="polite">
        {#each Array(6) as _, index (index)}
          <article class="animate-pulse rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex gap-3">
              <div class="h-16 w-16 rounded-full bg-slate-200"></div>
              <div class="flex-1 space-y-3 pt-1">
                <div class="h-4 w-3/4 rounded bg-slate-200"></div>
                <div class="h-3 w-1/2 rounded bg-slate-100"></div>
                <div class="flex gap-2">
                  <div class="h-6 w-20 rounded-full bg-slate-100"></div>
                  <div class="h-6 w-24 rounded-full bg-slate-100"></div>
                </div>
              </div>
            </div>
            <div class="mt-5 grid grid-cols-2 gap-3">
              <div class="h-14 rounded-lg bg-slate-100"></div>
              <div class="h-14 rounded-lg bg-slate-100"></div>
            </div>
            <div class="mt-4 h-10 rounded-md bg-slate-200"></div>
          </article>
        {/each}
      </section>
    {:else if filteredTherapists.length === 0}
      <section class="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
        <h2 class="text-base font-semibold text-slate-900">No therapists found</h2>
        <p class="mt-1 text-sm text-slate-500">Try a different search or specialty filter.</p>
      </section>
    {:else}
      <section
        class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
        aria-busy={isFiltering}
        aria-live="polite"
      >
        {#each filteredTherapists as therapist (therapist.id)}
          <article
            class={`flex h-full flex-col rounded-lg border p-4 shadow-sm transition ${
              therapist.is_available
                ? 'border-slate-200 bg-white hover:border-blue-200 hover:shadow-md'
                : 'border-slate-200 bg-slate-100 opacity-80'
            }`}
          >
            <div class="flex gap-3">
              <div class="relative h-16 w-16 shrink-0">
                {#if therapist.avatar_url && !failedAvatarIds.has(therapist.id)}
                  <img
                    src={therapist.avatar_url}
                    alt={`${therapist.name} avatar`}
                    class={`h-16 w-16 rounded-full object-cover ring-2 ring-white ${
                      therapist.is_available ? '' : 'grayscale'
                    }`}
                    loading="lazy"
                    onerror={() => markAvatarFailed(therapist.id)}
                  />
                {:else}
                  <div
                    class={`flex h-16 w-16 items-center justify-center rounded-full text-base font-bold ring-2 ring-white ${getAvatarFallbackClass(
                      therapist
                    )}`}
                    aria-label={`${therapist.name} initials`}
                  >
                    {getInitials(therapist.name)}
                  </div>
                {/if}
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <h2 class="truncate text-base font-semibold text-slate-950">{therapist.name}</h2>
                    <p class="mt-1 flex items-center gap-1 text-sm text-slate-500">
                      <Icon name="clock" size={15} />
                      {formatExperience(therapist.years_of_experience)}
                    </p>
                  </div>

                  <span
                    class={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${
                      therapist.is_available
                        ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100'
                        : 'bg-slate-200 text-slate-600 ring-1 ring-slate-300'
                    }`}
                  >
                    {therapist.is_available ? 'Available' : 'Unavailable'}
                  </span>
                </div>
              </div>
            </div>

            <div class="mt-4 flex min-h-8 flex-wrap gap-2">
              {#if therapist.specialties.length > 0}
                {#each therapist.specialties as specialty (specialty.id)}
                  <span class="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                    {specialty.name}
                  </span>
                {/each}
              {:else}
                <span class="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-500">
                  Specialty pending
                </span>
              {/if}
            </div>

            <div class="mt-5 grid grid-cols-2 gap-3">
              <div class="rounded-lg border border-slate-200 bg-white p-3">
                <p class="text-xs font-medium uppercase text-slate-400">Fee</p>
                <p class="mt-1 text-sm font-semibold text-slate-950">{formatFee(therapist.consultation_fee)}</p>
              </div>
              <div class="rounded-lg border border-slate-200 bg-white p-3">
                <p class="text-xs font-medium uppercase text-slate-400">Session</p>
                <p class="mt-1 text-sm font-semibold text-slate-950">50 minutes</p>
              </div>
            </div>

            <div class="mt-auto flex flex-col gap-2 pt-4">
              <a
                href={`/therapist/${therapist.id}`}
                class="inline-flex h-9 items-center justify-center rounded-md border border-blue-100 bg-blue-50 px-3 text-sm font-semibold text-blue-700 hover:border-blue-200 hover:bg-blue-100"
              >
                View full profile
              </a>

              {#if therapist.is_available}
                <Button
                  onclick={() => openBookingModal(therapist)}
                  class="h-10 w-full bg-blue-600 text-white hover:bg-blue-700"
                >
                  Book appointment
                </Button>
              {:else}
                <div
                  class="flex h-10 w-full items-center justify-center rounded-md bg-slate-200 text-sm font-semibold text-slate-500"
                  role="status"
                >
                  Unavailable
                </div>
              {/if}
            </div>
          </article>
        {/each}
      </section>
    {/if}
  </main>
</div>

{#if showBookingModal && selectedTherapist}
  <div class="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/50 p-4 sm:items-center">
    <Card className="w-full max-w-md rounded-lg border-slate-200">
      <CardContent className="space-y-4 p-5">
        <div>
          <h3 class="text-lg font-bold text-slate-950">Book with {selectedTherapist.name}</h3>
          <p class="mt-1 text-sm text-slate-500">
            {formatExperience(selectedTherapist.years_of_experience)} · {formatFee(selectedTherapist.consultation_fee)}
          </p>
        </div>

        <form use:enhance method="POST" class="space-y-4">
          <div class="space-y-1">
            <Label forValue="scheduled_at">Date and time</Label>
            <Input id="scheduled_at" type="datetime-local" bind:value={$form.scheduled_at} />
            {#if $errors.scheduled_at}
              <p class="text-xs text-red-500">{$errors.scheduled_at}</p>
            {/if}
          </div>

          <div class="space-y-1">
            <Label forValue="appointment_type">Session type</Label>
            <Select id="appointment_type" bind:value={$form.appointment_type}>
              <option value="video">Video call</option>
              <option value="phone">Phone call</option>
              <option value="in_person">In person</option>
            </Select>
          </div>

          <div class="space-y-1">
            <Label forValue="reason">Reason (optional)</Label>
            <Textarea
              id="reason"
              rows="3"
              bind:value={$form.reason}
              placeholder="Briefly describe what you would like to discuss"
              className="resize-none"
            />
          </div>

          <div class="flex gap-3">
            <Button
              type="button"
              onclick={() => (showBookingModal = false)}
              class="flex-1 border-slate-200"
              variant="outline"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={$submitting} class="flex-1 bg-blue-600 text-white hover:bg-blue-700">
              {#if $submitting}
                <Icon name="spinner" class="animate-spin" size={16} />
              {/if}
              Confirm
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
{/if}
