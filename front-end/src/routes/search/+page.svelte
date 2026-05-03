<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { toast } from 'svelte-sonner';
  import { ApiError, therapyApi } from '$lib/api';
  import { SearchInput } from '$lib/components/ui/search-input';
  import { Button } from '$lib/components/ui/button';
  import type { Specialty, Therapist } from '$lib/types';

  const allSpecialtiesSlug = 'all';
  const pageSize = 12;
  const avatarFallbackClasses = [
    'bg-blue-100 text-blue-700',
    'bg-emerald-100 text-emerald-700',
    'bg-cyan-100 text-cyan-700',
    'bg-amber-100 text-amber-800',
    'bg-rose-100 text-rose-700',
    'bg-slate-100 text-slate-700'
  ];

  let searchQuery = $state('');
  let activeSpecialty = $state(allSpecialtiesSlug);
  let specialties = $state<Specialty[]>([]);
  let therapists = $state<Therapist[]>([]);
  let failedAvatarIds = $state<Set<string>>(new Set());
  let totalCount = $state(0);
  let currentPage = $state(1);
  let isInitialLoading = $state(true);
  let isLoadingMore = $state(false);
  let hasHydrated = false;
  let lastAppliedFilterKey = '';
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;
  let therapistRequestId = 0;

  let activeSpecialtyName = $derived(
    activeSpecialty === allSpecialtiesSlug
      ? 'All specialties'
      : specialties.find((specialty) => specialty.slug === activeSpecialty)?.name ?? 'Selected specialty'
  );

  let hasMore = $derived(therapists.length < totalCount);
  let resultLabel = $derived(`${totalCount} ${totalCount === 1 ? 'therapist' : 'therapists'} found`);
  let emptyQueryLabel = $derived(searchQuery.trim());

  function filterKey() {
    return `${searchQuery.trim()}::${activeSpecialty}`;
  }

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

  function buildUrl() {
    const params = new URLSearchParams();
    const query = searchQuery.trim();

    if (query) params.set('search', query);
    if (activeSpecialty !== allSpecialtiesSlug) params.set('specialty', activeSpecialty);

    const queryString = params.toString();
    return queryString ? `/search?${queryString}` : '/search';
  }

  async function syncUrl() {
    const nextUrl = buildUrl();
    const currentUrl = `${$page.url.pathname}${$page.url.search}`;

    if (currentUrl !== nextUrl) {
      await goto(nextUrl, {
        replaceState: true,
        noScroll: true,
        keepFocus: true
      });
    }
  }

  async function loadTherapists({ reset }: { reset: boolean }) {
    const requestId = ++therapistRequestId;
    const pageToLoad = reset ? 1 : currentPage + 1;

    if (reset) {
      isInitialLoading = true;
    } else {
      isLoadingMore = true;
    }

    try {
      const response = await therapyApi.listTherapists({
        search: searchQuery.trim() || undefined,
        specialty: activeSpecialty === allSpecialtiesSlug ? undefined : activeSpecialty,
        page: pageToLoad,
        page_size: pageSize
      });

      if (requestId !== therapistRequestId) return;

      therapists = reset ? response.results : [...therapists, ...response.results];
      totalCount = response.count;
      currentPage = pageToLoad;
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to load therapists.');
    } finally {
      if (requestId === therapistRequestId) {
        isInitialLoading = false;
        isLoadingMore = false;
      }
    }
  }

  async function applyFilters() {
    await syncUrl();
    await loadTherapists({ reset: true });
  }

  function applyFiltersNow() {
    if (debounceTimer) clearTimeout(debounceTimer);
    lastAppliedFilterKey = filterKey();
    void applyFilters();
  }

  function clearFilters() {
    searchQuery = '';
    activeSpecialty = allSpecialtiesSlug;
    applyFiltersNow();
  }

  function selectSpecialty(slug: string) {
    if (activeSpecialty === slug) return;
    activeSpecialty = slug;
    applyFiltersNow();
  }

  $effect(() => {
    if (!hasHydrated) return;

    const nextFilterKey = filterKey();
    if (nextFilterKey === lastAppliedFilterKey) return;

    lastAppliedFilterKey = nextFilterKey;

    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      void applyFilters();
    }, 300);
  });

  onMount(async () => {
    const params = $page.url.searchParams;
    searchQuery = params.get('search') ?? '';
    activeSpecialty = params.get('specialty') ?? allSpecialtiesSlug;
    lastAppliedFilterKey = filterKey();
    hasHydrated = true;

    try {
      const [specialtyResponse] = await Promise.all([
        therapyApi.listSpecialties(),
        loadTherapists({ reset: true })
      ]);

      specialties = specialtyResponse.results;
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to load search filters.');
    }
  });

  onDestroy(() => {
    if (debounceTimer) clearTimeout(debounceTimer);
  });
</script>

<svelte:head>
  <title>Find a Therapist - Online Therapy</title>
</svelte:head>

<section class="min-h-screen bg-slate-50">
  <div class="mx-auto max-w-7xl space-y-6 p-4 pb-12 sm:p-6 lg:p-8">
    <header class="space-y-2">
      <p class="text-sm font-semibold uppercase tracking-wide text-blue-600">Therapist discovery</p>
      <h1 class="text-2xl font-semibold text-slate-950 sm:text-3xl">Find the right therapist</h1>
      <p class="max-w-2xl text-sm leading-relaxed text-slate-600">
        Compare active therapist profiles across specialties, fees, and availability.
      </p>
    </header>

    <section class="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div class="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
        <SearchInput
          bind:value={searchQuery}
          placeholder="Search therapists, specialties, or focus areas"
          onSearch={(query) => {
            searchQuery = query;
            applyFiltersNow();
          }}
        />

        <div class="text-sm font-semibold text-slate-600">{resultLabel}</div>
      </div>

      <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide" aria-label="Specialty filters">
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
      </div>

      <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span class="rounded-full bg-slate-100 px-3 py-1">Search: {searchQuery.trim() || 'Any'}</span>
        <span class="rounded-full bg-slate-100 px-3 py-1">Specialty: {activeSpecialtyName}</span>
        {#if searchQuery.trim() || activeSpecialty !== allSpecialtiesSlug}
          <button type="button" class="font-semibold text-blue-700 hover:text-blue-800" onclick={clearFilters}>
            Clear filters
          </button>
        {/if}
      </div>
    </section>

    {#if isInitialLoading}
      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3" aria-live="polite">
        {#each Array(6) as _, index (index)}
          <article class="animate-pulse rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex gap-3">
              <div class="h-16 w-16 rounded-full bg-slate-200"></div>
              <div class="flex-1 space-y-3 pt-1">
                <div class="h-4 w-3/4 rounded bg-slate-200"></div>
                <div class="h-3 w-1/2 rounded bg-slate-100"></div>
                <div class="h-6 w-32 rounded-full bg-slate-100"></div>
              </div>
            </div>
            <div class="mt-5 h-16 rounded-lg bg-slate-100"></div>
            <div class="mt-4 h-10 rounded-md bg-slate-200"></div>
          </article>
        {/each}
      </section>
    {:else if therapists.length === 0}
      <section class="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
        <h2 class="text-xl font-semibold text-slate-950">No therapists found for '{emptyQueryLabel}'</h2>
        <p class="mx-auto mt-2 max-w-md text-sm leading-relaxed text-slate-500">
          Try searching for a therapist name, a broader specialty, or clearing the selected specialty filter.
        </p>
        <a
          href="/search"
          class="mt-5 inline-flex text-sm font-semibold text-blue-700 hover:text-blue-800"
          onclick={(event) => {
            event.preventDefault();
            clearFilters();
          }}
        >
          Clear filters
        </a>
      </section>
    {:else}
      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3" aria-live="polite">
        {#each therapists as therapist (therapist.id)}
          <article
            class={`flex h-full flex-col rounded-lg border p-4 shadow-sm transition ${
              therapist.is_available
                ? 'border-slate-200 bg-white hover:border-blue-200 hover:shadow-md'
                : 'border-slate-200 bg-slate-100 opacity-80'
            }`}
          >
            <div class="flex gap-3">
              <div class="h-16 w-16 shrink-0">
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
                    <p class="mt-1 text-sm text-slate-500">{formatExperience(therapist.years_of_experience)}</p>
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

            <div class="mt-5 rounded-lg border border-slate-200 bg-white p-3">
              <p class="text-xs font-medium uppercase text-slate-400">Consultation fee</p>
              <p class="mt-1 text-sm font-semibold text-slate-950">{formatFee(therapist.consultation_fee)}</p>
            </div>

            <div class="mt-auto pt-4">
              <a
                href={`/therapist/${therapist.id}`}
                class="inline-flex h-10 w-full items-center justify-center rounded-md bg-blue-600 px-3 text-sm font-semibold text-white hover:bg-blue-700"
              >
                View profile
              </a>
            </div>
          </article>
        {/each}
      </section>

      {#if hasMore}
        <div class="flex justify-center pt-2">
          <Button
            variant="outline"
            class="border-blue-200 text-blue-700 hover:bg-blue-50"
            disabled={isLoadingMore}
            onclick={() => loadTherapists({ reset: false })}
          >
            {isLoadingMore ? 'Loading...' : 'Load more therapists'}
          </Button>
        </div>
      {/if}
    {/if}
  </div>
</section>
