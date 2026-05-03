<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { ApiError, apiClient } from '$lib/api/client';
  import { therapyApi } from '$lib/api/appointments';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';
  import type { PaginatedResponse, Specialty } from '$lib/types';
  import { formatExperience, formatFee } from '$lib/utils/therapy';

  type TherapistAdminStatus = 'all' | 'active' | 'inactive' | 'available' | 'unavailable';

  interface AdminTherapist {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    bio: string;
    specialties: string[];
    years_of_experience: number;
    consultation_fee: string | null;
    license_number: string;
    is_active: boolean;
    is_available: boolean;
    created_at: string;
    updated_at: string;
  }

  interface TherapistForm {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    bio: string;
    specialtyIds: string[];
    consultationFee: string;
    licenseNumber: string;
    yearsOfExperience: number;
    isAvailable: boolean;
  }

  interface AdminTherapistCreatePayload {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    bio?: string;
    specialties?: string[];
    consultation_fee?: number | null;
    license_number?: string;
    years_of_experience?: number;
    is_available?: boolean;
  }

  interface AdminTherapistUpdatePayload {
    bio?: string;
    specialties?: string[];
    consultation_fee?: number | null;
    license_number?: string;
    years_of_experience?: number;
    is_available?: boolean;
  }

  const emptyForm: TherapistForm = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    bio: '',
    specialtyIds: [],
    consultationFee: '',
    licenseNumber: '',
    yearsOfExperience: 0,
    isAvailable: true
  };

  let therapists = $state<AdminTherapist[]>([]);
  let specialties = $state<Specialty[]>([]);
  let searchQuery = $state('');
  let statusFilter = $state<TherapistAdminStatus>('all');
  let currentPage = $state(1);
  let pageSize = $state(12);
  let totalPages = $state(1);
  let totalTherapists = $state(0);

  let isLoading = $state(true);
  let loadError = $state<string | null>(null);
  let showCreateDrawer = $state(false);
  let showEditDrawer = $state(false);
  let showDeactivateConfirm = $state(false);
  let isCreating = $state(false);
  let isSaving = $state(false);
  let isDeactivating = $state(false);
  let updatingTherapistId = $state<string | null>(null);
  let form = $state<TherapistForm>({ ...emptyForm });
  let editTarget = $state<AdminTherapist | null>(null);
  let deactivateTarget = $state<AdminTherapist | null>(null);
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  let activeCount = $derived(therapists.filter((therapist) => therapist.is_active).length);
  let inactiveCount = $derived(therapists.filter((therapist) => !therapist.is_active).length);
  let availableCount = $derived(therapists.filter((therapist) => therapist.is_available).length);

  function getErrorMessage(error: unknown, fallback: string) {
    if (error instanceof ApiError) return error.message;
    if (error instanceof Error) return error.message;
    return fallback;
  }

  function fullName(therapist: AdminTherapist) {
    return `${therapist.first_name} ${therapist.last_name}`.trim() || therapist.email;
  }

  function initials(name: string) {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? '')
      .join('');
  }

  function resetForm() {
    form = { ...emptyForm, specialtyIds: [] };
  }

  function selectedSpecialtyNames(ids: string[]) {
    return specialties
      .filter((specialty) => ids.includes(specialty.id))
      .map((specialty) => specialty.name);
  }

  function buildCreatePayload(): AdminTherapistCreatePayload {
    return {
      email: form.email.trim().toLowerCase(),
      password: form.password,
      first_name: form.firstName.trim(),
      last_name: form.lastName.trim(),
      bio: form.bio.trim(),
      specialties: form.specialtyIds,
      consultation_fee: form.consultationFee.trim() ? Number(form.consultationFee) : null,
      license_number: form.licenseNumber.trim(),
      years_of_experience: Number(form.yearsOfExperience) || 0,
      is_available: form.isAvailable
    };
  }

  function buildUpdatePayload(): AdminTherapistUpdatePayload {
    return {
      bio: form.bio.trim(),
      specialties: form.specialtyIds,
      consultation_fee: form.consultationFee.trim() ? Number(form.consultationFee) : null,
      license_number: form.licenseNumber.trim(),
      years_of_experience: Number(form.yearsOfExperience) || 0,
      is_available: form.isAvailable
    };
  }

  function validateCreateForm() {
    if (!form.firstName.trim() || !form.lastName.trim() || !form.email.trim() || !form.password) {
      toast.error('First name, last name, email, and password are required.');
      return false;
    }

    return validateProfileFields();
  }

  function validateProfileFields() {
    if (form.consultationFee.trim()) {
      const fee = Number(form.consultationFee);
      if (!Number.isFinite(fee) || fee < 0) {
        toast.error('Consultation fee must be a valid non-negative number.');
        return false;
      }
    }

    if (!Number.isFinite(Number(form.yearsOfExperience)) || Number(form.yearsOfExperience) < 0) {
      toast.error('Years of experience must be zero or higher.');
      return false;
    }

    return true;
  }

  function toggleSpecialty(id: string) {
    form.specialtyIds = form.specialtyIds.includes(id)
      ? form.specialtyIds.filter((specialtyId) => specialtyId !== id)
      : [...form.specialtyIds, id];
  }

  async function loadSpecialties() {
    const response = await therapyApi.listSpecialties();
    specialties = response.results;
  }

  async function loadTherapists(options: { showLoading?: boolean } = {}) {
    const { showLoading = true } = options;
    if (showLoading) isLoading = true;
    loadError = null;

    const params = new URLSearchParams({
      page: String(currentPage),
      page_size: String(pageSize)
    });

    if (searchQuery.trim()) params.set('q', searchQuery.trim());
    if (statusFilter !== 'all') params.set('status', statusFilter);

    try {
      const response = await apiClient.get<PaginatedResponse<AdminTherapist>>(
        `/admin/therapists/?${params.toString()}`
      );
      therapists = response.results;
      totalTherapists = response.count;
      totalPages = Math.max(1, Math.ceil(response.count / pageSize));
    } catch (error) {
      loadError = getErrorMessage(error, 'Failed to load therapists.');
      toast.error(loadError);
    } finally {
      isLoading = false;
    }
  }

  async function loadInitialData() {
    isLoading = true;
    try {
      await Promise.all([loadSpecialties(), loadTherapists({ showLoading: false })]);
    } catch (error) {
      loadError = getErrorMessage(error, 'Failed to load therapist management data.');
      toast.error(loadError);
    } finally {
      isLoading = false;
    }
  }

  function onSearchInput(value: string) {
    searchQuery = value;
    currentPage = 1;
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => loadTherapists({ showLoading: false }), 300);
  }

  function changeStatusFilter(filter: TherapistAdminStatus) {
    statusFilter = filter;
    currentPage = 1;
    loadTherapists();
  }

  function goToPage(page: number) {
    currentPage = page;
    loadTherapists();
  }

  function openCreateDrawer() {
    resetForm();
    showCreateDrawer = true;
  }

  function closeCreateDrawer() {
    showCreateDrawer = false;
  }

  function openEditDrawer(therapist: AdminTherapist) {
    editTarget = therapist;
    form = {
      ...emptyForm,
      bio: therapist.bio ?? '',
      specialtyIds: specialties
        .filter((specialty) => therapist.specialties.includes(specialty.name))
        .map((specialty) => specialty.id),
      consultationFee: therapist.consultation_fee ?? '',
      licenseNumber: therapist.license_number ?? '',
      yearsOfExperience: therapist.years_of_experience ?? 0,
      isAvailable: therapist.is_available
    };
    showEditDrawer = true;
  }

  function closeEditDrawer() {
    showEditDrawer = false;
    editTarget = null;
  }

  async function createTherapist() {
    if (!validateCreateForm()) return;

    isCreating = true;
    try {
      await apiClient.post<AdminTherapist>('/admin/therapists/', buildCreatePayload());
      toast.success('Therapist user and profile created.');
      showCreateDrawer = false;
      currentPage = 1;
      await loadTherapists();
    } catch (error) {
      toast.error(getErrorMessage(error, 'Failed to create therapist.'));
    } finally {
      isCreating = false;
    }
  }

  async function saveTherapistProfile() {
    if (!editTarget || !validateProfileFields()) return;

    isSaving = true;
    try {
      const updated = await apiClient.patch<AdminTherapist>(
        `/admin/therapists/${editTarget.id}/`,
        buildUpdatePayload()
      );
      therapists = therapists.map((therapist) => (therapist.id === updated.id ? updated : therapist));
      toast.success(`${fullName(updated)} was updated.`);
      closeEditDrawer();
    } catch (error) {
      toast.error(getErrorMessage(error, 'Failed to update therapist.'));
    } finally {
      isSaving = false;
    }
  }

  async function toggleAvailability(therapist: AdminTherapist) {
    updatingTherapistId = therapist.id;
    try {
      const updated = await apiClient.patch<AdminTherapist>(`/admin/therapists/${therapist.id}/`, {
        is_available: !therapist.is_available
      });
      therapists = therapists.map((item) => (item.id === updated.id ? updated : item));
      toast.success(`${fullName(updated)} is now ${updated.is_available ? 'available' : 'unavailable'}.`);
    } catch (error) {
      toast.error(getErrorMessage(error, 'Failed to update availability.'));
    } finally {
      updatingTherapistId = null;
    }
  }

  function requestDeactivate(therapist: AdminTherapist) {
    deactivateTarget = therapist;
    showDeactivateConfirm = true;
  }

  function cancelDeactivate() {
    showDeactivateConfirm = false;
    deactivateTarget = null;
  }

  async function confirmDeactivate() {
    if (!deactivateTarget) return;

    isDeactivating = true;
    try {
      await apiClient.delete<unknown>(`/admin/therapists/${deactivateTarget.id}/`);
      toast.success(`${fullName(deactivateTarget)} has been deactivated.`);
      showDeactivateConfirm = false;
      deactivateTarget = null;
      await loadTherapists();
    } catch (error) {
      toast.error(getErrorMessage(error, 'Failed to deactivate therapist.'));
    } finally {
      isDeactivating = false;
    }
  }

  function statusPillClass(isActive: boolean) {
    return isActive
      ? 'border-emerald-200 bg-emerald-100 text-emerald-700'
      : 'border-slate-200 bg-slate-100 text-slate-700';
  }

  function availabilityPillClass(isAvailable: boolean) {
    return isAvailable
      ? 'border-blue-200 bg-blue-50 text-blue-700'
      : 'border-slate-200 bg-slate-50 text-slate-600';
  }

  onMount(loadInitialData);
</script>

<svelte:head>
  <title>Admin • Therapist Management — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Admin Console</p>
    <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">Therapist Management</h1>
        <p class="mt-1 text-sm text-slate-600">
          Manage therapist users, profile completeness data, specialties, pricing, and availability.
        </p>
      </div>
      <Button class="bg-blue-600 text-white hover:bg-blue-700" onclick={openCreateDrawer}>
        Add Therapist
      </Button>
    </div>
  </header>

  <div class="grid gap-4 sm:grid-cols-4">
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Total therapists</p>
      <p class="mt-2 text-2xl font-semibold text-blue-900">{totalTherapists}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Active on page</p>
      <p class="mt-2 text-2xl font-semibold text-emerald-700">{activeCount}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Inactive on page</p>
      <p class="mt-2 text-2xl font-semibold text-slate-700">{inactiveCount}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Available on page</p>
      <p class="mt-2 text-2xl font-semibold text-blue-700">{availableCount}</p>
    </article>
  </div>

  <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
    <div class="flex flex-wrap items-center gap-3">
      <div class="min-w-[240px] flex-1">
        <Input
          type="search"
          value={searchQuery}
          className="h-11 border-blue-200"
          placeholder="Search by therapist name or email"
          oninput={(event: Event) => onSearchInput((event.currentTarget as HTMLInputElement).value)}
        />
      </div>

      <div class="inline-flex flex-wrap rounded-lg border border-blue-200 bg-white p-1 text-sm">
        {#each ['all', 'active', 'inactive', 'available', 'unavailable'] as filter}
          <button
            type="button"
            class={`rounded-md px-3 py-1.5 capitalize transition ${statusFilter === filter ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
            onclick={() => changeStatusFilter(filter as TherapistAdminStatus)}
          >
            {filter}
          </button>
        {/each}
      </div>
    </div>

    {#if isLoading}
      <div class="space-y-3">
        {#each Array.from({ length: 6 }) as _, index (index)}
          <div class="h-20 animate-pulse rounded-xl border border-slate-100 bg-slate-50"></div>
        {/each}
      </div>
    {:else if loadError}
      <div class="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center">
        <p class="text-sm text-rose-700">{loadError}</p>
        <Button class="mt-4" onclick={() => loadInitialData()}>Retry</Button>
      </div>
    {:else}
      <div class="overflow-x-auto rounded-xl border border-slate-200">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
            <tr>
              <th class="px-4 py-3">Therapist</th>
              <th class="px-4 py-3">Specialties</th>
              <th class="px-4 py-3">Fee</th>
              <th class="px-4 py-3">License</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            {#each therapists as therapist (therapist.id)}
              <tr class={!therapist.is_active ? 'bg-slate-50 text-slate-500' : 'hover:bg-blue-50/40'}>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                      {initials(fullName(therapist))}
                    </div>
                    <div>
                      <p class="font-medium text-slate-900">{fullName(therapist)}</p>
                      <p class="text-xs text-slate-500">{therapist.email}</p>
                      <p class="mt-0.5 text-xs text-slate-500">
                        {formatExperience(therapist.years_of_experience)}
                      </p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  {#if therapist.specialties.length > 0}
                    <div class="flex max-w-xs flex-wrap gap-1.5">
                      {#each therapist.specialties as spec (spec)}
                        <span class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                          {spec}
                        </span>
                      {/each}
                    </div>
                  {:else}
                    <span class="text-xs text-slate-400">No specialties</span>
                  {/if}
                </td>
                <td class="px-4 py-3 text-slate-700">{formatFee(therapist.consultation_fee)}</td>
                <td class="px-4 py-3 text-slate-700">
                  {therapist.license_number || 'Not set'}
                </td>
                <td class="px-4 py-3">
                  <div class="flex flex-wrap gap-1.5">
                    <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${statusPillClass(therapist.is_active)}`}>
                      {therapist.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${availabilityPillClass(therapist.is_available)}`}>
                      {therapist.is_available ? 'Available' : 'Unavailable'}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex flex-wrap justify-end gap-2">
                    <Button type="button" variant="outline" class="border-slate-200" onclick={() => openEditDrawer(therapist)}>
                      Edit
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      class="border-blue-200 text-blue-700 hover:bg-blue-50"
                      onclick={() => toggleAvailability(therapist)}
                      disabled={updatingTherapistId === therapist.id || !therapist.is_active}
                    >
                      {therapist.is_available ? 'Set unavailable' : 'Set available'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      class="border-rose-200 text-rose-700 hover:bg-rose-50"
                      onclick={() => requestDeactivate(therapist)}
                      disabled={!therapist.is_active}
                    >
                      Deactivate
                    </Button>
                  </div>
                </td>
              </tr>
            {/each}

            {#if therapists.length === 0}
              <tr>
                <td colspan="6" class="px-4 py-10 text-center text-slate-500">
                  No therapists match your current filters.
                </td>
              </tr>
            {/if}
          </tbody>
        </table>
      </div>

      {#if totalPages > 1}
        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4">
          <p class="text-sm text-slate-600">
            Page {currentPage} of {totalPages} ({totalTherapists} total therapists)
          </p>
          <div class="flex gap-2">
            <Button variant="outline" disabled={currentPage === 1} onclick={() => goToPage(currentPage - 1)}>
              Previous
            </Button>
            <Button variant="outline" disabled={currentPage === totalPages} onclick={() => goToPage(currentPage + 1)}>
              Next
            </Button>
          </div>
        </div>
      {/if}
    {/if}
  </section>

  {#snippet profileFields(includeAccountFields: boolean)}
    {#if includeAccountFields}
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="space-y-2">
          <Label class="font-medium text-slate-800">First name *</Label>
          <Input bind:value={form.firstName} className="h-11 border-blue-200" placeholder="Lena" />
        </div>
        <div class="space-y-2">
          <Label class="font-medium text-slate-800">Last name *</Label>
          <Input bind:value={form.lastName} className="h-11 border-blue-200" placeholder="Whitmore" />
        </div>
      </div>

      <div class="space-y-2">
        <Label class="font-medium text-slate-800">Email *</Label>
        <Input type="email" bind:value={form.email} className="h-11 border-blue-200" placeholder="lena@example.com" />
      </div>

      <div class="space-y-2">
        <Label class="font-medium text-slate-800">Temporary password *</Label>
        <Input type="password" bind:value={form.password} className="h-11 border-blue-200" placeholder="Minimum 8 characters" />
      </div>
    {/if}

    <div class="space-y-2">
      <Label class="font-medium text-slate-800">Bio</Label>
      <Textarea bind:value={form.bio} className="min-h-28 border-blue-200" placeholder="Therapeutic approach, populations served, and care style." />
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <div class="space-y-2">
        <Label class="font-medium text-slate-800">Consultation fee</Label>
        <Input type="number" bind:value={form.consultationFee} className="h-11 border-blue-200" min="0" step="0.01" placeholder="110.00" />
      </div>
      <div class="space-y-2">
        <Label class="font-medium text-slate-800">Years of experience</Label>
        <Input type="number" bind:value={form.yearsOfExperience} className="h-11 border-blue-200" min="0" step="1" />
      </div>
      <div class="space-y-2">
        <Label class="font-medium text-slate-800">License number</Label>
        <Input bind:value={form.licenseNumber} className="h-11 border-blue-200" placeholder="LIC-12345" />
      </div>
    </div>

    <div class="space-y-2">
      <Label class="font-medium text-slate-800">Specialties</Label>
      <div class="flex flex-wrap gap-2 rounded-xl border border-blue-100 bg-blue-50/40 p-3">
        {#each specialties as specialty (specialty.id)}
          <button
            type="button"
            class={`rounded-full border px-3 py-1.5 text-sm transition ${form.specialtyIds.includes(specialty.id) ? 'border-blue-600 bg-blue-600 text-white' : 'border-blue-200 bg-white text-blue-700 hover:bg-blue-50'}`}
            onclick={() => toggleSpecialty(specialty.id)}
          >
            {specialty.name}
          </button>
        {/each}

        {#if specialties.length === 0}
          <span class="text-sm text-slate-500">No specialties are available yet.</span>
        {/if}
      </div>
      {#if form.specialtyIds.length > 0}
        <p class="text-xs text-slate-500">
          Selected: {selectedSpecialtyNames(form.specialtyIds).join(', ')}
        </p>
      {/if}
    </div>

    <label class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
      <input type="checkbox" bind:checked={form.isAvailable} class="h-4 w-4 rounded border-slate-300 text-blue-600" />
      Show therapist as available for booking
    </label>
  {/snippet}

  {#if showCreateDrawer}
    <div class="fixed inset-0 z-50 flex">
      <button
        type="button"
        class="h-full w-full bg-black/40"
        onclick={closeCreateDrawer}
        aria-label="Close create therapist panel"
      ></button>

      <aside class="h-full w-full max-w-2xl space-y-5 overflow-y-auto border-l border-blue-100 bg-white p-5 shadow-xl sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-blue-950">Create Therapist</h2>
            <p class="mt-1 text-sm text-slate-600">
              Creates the therapist user and professional profile through the admin API.
            </p>
          </div>
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeCreateDrawer}>Close</Button>
        </div>

        <div class="space-y-4">
          {@render profileFields(true)}
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeCreateDrawer}>Cancel</Button>
          <Button type="button" class="bg-blue-600 text-white hover:bg-blue-700" onclick={createTherapist} disabled={isCreating}>
            {isCreating ? 'Creating...' : 'Create Therapist'}
          </Button>
        </div>
      </aside>
    </div>
  {/if}

  {#if showEditDrawer && editTarget}
    <div class="fixed inset-0 z-50 flex">
      <button
        type="button"
        class="h-full w-full bg-black/40"
        onclick={closeEditDrawer}
        aria-label="Close edit therapist panel"
      ></button>

      <aside class="h-full w-full max-w-2xl space-y-5 overflow-y-auto border-l border-blue-100 bg-white p-5 shadow-xl sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-blue-950">Edit Therapist Profile</h2>
            <p class="mt-1 text-sm text-slate-600">{fullName(editTarget)} · {editTarget.email}</p>
          </div>
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeEditDrawer}>Close</Button>
        </div>

        <div class="space-y-4">
          {@render profileFields(false)}
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeEditDrawer}>Cancel</Button>
          <Button type="button" class="bg-blue-600 text-white hover:bg-blue-700" onclick={saveTherapistProfile} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </aside>
    </div>
  {/if}

  {#if showDeactivateConfirm && deactivateTarget}
    <div class="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <article class="w-full max-w-md space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
        <h3 class="text-lg font-semibold text-slate-900">Deactivate therapist?</h3>
        <p class="text-sm text-slate-600">
          This deactivates <span class="font-medium">{fullName(deactivateTarget)}</span> and removes them from public therapist discovery.
        </p>

        <div class="flex justify-end gap-2">
          <Button type="button" variant="outline" class="border-slate-200" onclick={cancelDeactivate}>Keep Active</Button>
          <Button type="button" class="bg-rose-600 text-white hover:bg-rose-700" onclick={confirmDeactivate} disabled={isDeactivating}>
            {isDeactivating ? 'Deactivating...' : 'Deactivate'}
          </Button>
        </div>
      </article>
    </div>
  {/if}
</section>
