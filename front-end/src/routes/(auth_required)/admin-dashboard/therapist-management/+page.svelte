<script lang="ts">
  import { toast } from 'svelte-sonner';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';

  type TherapistStatus = 'active' | 'inactive';

  interface TherapistAdminItem {
    id: string;
    user: {
      id: string;
      full_name: string;
      email: string;
      is_staff: boolean;
      is_superuser: boolean;
    };
    profile: {
      bio: string;
      specialties: string[];
      hourly_rate: number;
      status: TherapistStatus;
      created_at: string;
    };
  }

  interface CreateTherapistForm {
    name: string;
    email: string;
    password: string;
    bio: string;
    specialties: string;
    hourlyRate: string;
  }

  const seedTherapists: TherapistAdminItem[] = [
    {
      id: 'th-1001',
      user: {
        id: 'usr-1001',
        full_name: 'Dr. Lena Whitmore',
        email: 'lena.whitmore@therapy.local',
        is_staff: true,
        is_superuser: false
      },
      profile: {
        bio: 'Trauma-informed therapist focused on anxiety, burnout, and emotional regulation.',
        specialties: ['Anxiety', 'Trauma', 'Burnout'],
        hourly_rate: 110,
        status: 'active',
        created_at: '2026-01-05T09:00:00.000Z'
      }
    },
    {
      id: 'th-1002',
      user: {
        id: 'usr-1002',
        full_name: 'Dr. Jordan Hale',
        email: 'jordan.hale@therapy.local',
        is_staff: true,
        is_superuser: false
      },
      profile: {
        bio: 'CBT practitioner supporting adults with mood disorders and sleep routines.',
        specialties: ['CBT', 'Depression', 'Sleep'],
        hourly_rate: 95,
        status: 'active',
        created_at: '2026-02-12T09:00:00.000Z'
      }
    },
    {
      id: 'th-1003',
      user: {
        id: 'usr-1003',
        full_name: 'Dr. Maya Okoro',
        email: 'maya.okoro@therapy.local',
        is_staff: true,
        is_superuser: false
      },
      profile: {
        bio: 'Family and relationship therapist. Specializes in communication frameworks.',
        specialties: ['Family', 'Relationships'],
        hourly_rate: 120,
        status: 'inactive',
        created_at: '2026-02-27T09:00:00.000Z'
      }
    }
  ];

  let therapists = $state<TherapistAdminItem[]>(seedTherapists);
  let searchQuery = $state('');
  let statusFilter = $state<'all' | TherapistStatus>('all');

  let showCreateDrawer = $state(false);
  let isCreating = $state(false);

  let showDeleteConfirm = $state(false);
  let deleteTarget = $state<TherapistAdminItem | null>(null);
  let isDeleting = $state(false);

  const emptyForm: CreateTherapistForm = {
    name: '',
    email: '',
    password: '',
    bio: '',
    specialties: '',
    hourlyRate: ''
  };

  let form = $state<CreateTherapistForm>({ ...emptyForm });

  let filteredTherapists = $derived.by(() => {
    const q = searchQuery.trim().toLowerCase();
    return therapists
      .filter((item) => statusFilter === 'all' || item.profile.status === statusFilter)
      .filter((item) => {
        if (!q) return true;
        return (
          item.user.full_name.toLowerCase().includes(q) ||
          item.user.email.toLowerCase().includes(q) ||
          item.profile.specialties.some((s) => s.toLowerCase().includes(q))
        );
      })
      .sort((a, b) => +new Date(b.profile.created_at) - +new Date(a.profile.created_at));
  });

  let activeCount = $derived(therapists.filter((t) => t.profile.status === 'active').length);
  let inactiveCount = $derived(therapists.filter((t) => t.profile.status === 'inactive').length);

  function resetForm() {
    form = { ...emptyForm };
  }

  function openCreateDrawer() {
    resetForm();
    showCreateDrawer = true;
  }

  function closeCreateDrawer() {
    showCreateDrawer = false;
  }

  function parseSpecialties(value: string) {
    return value
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean);
  }

  async function createTherapist() {
    const specialties = parseSpecialties(form.specialties);
    const hourlyRate = Number(form.hourlyRate);

    if (!form.name.trim() || !form.email.trim() || !form.password || specialties.length === 0) {
      toast.error('Please complete all required fields before creating a therapist.');
      return;
    }

    if (!Number.isFinite(hourlyRate) || hourlyRate <= 0) {
      toast.error('Hourly rate must be a positive number.');
      return;
    }

    if (therapists.some((t) => t.user.email.toLowerCase() === form.email.trim().toLowerCase())) {
      toast.error('A therapist with this email already exists.');
      return;
    }

    isCreating = true;

    const payload = {
      user: {
        full_name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        is_staff: true,
        is_superuser: false
      },
      therapist_profile: {
        bio: form.bio.trim(),
        specialties,
        hourly_rate: hourlyRate
      }
    };

    await new Promise((resolve) => setTimeout(resolve, 450));

    const nextId = `th-${Date.now()}`;
    therapists = [
      {
        id: nextId,
        user: {
          id: `usr-${Date.now()}`,
          full_name: payload.user.full_name,
          email: payload.user.email,
          is_staff: payload.user.is_staff,
          is_superuser: payload.user.is_superuser
        },
        profile: {
          bio: payload.therapist_profile.bio,
          specialties: payload.therapist_profile.specialties,
          hourly_rate: payload.therapist_profile.hourly_rate,
          status: 'active',
          created_at: new Date().toISOString()
        }
      },
      ...therapists
    ];

    isCreating = false;
    showCreateDrawer = false;
    toast.success('Therapist user and profile created successfully.');
  }

  function requestDelete(item: TherapistAdminItem) {
    deleteTarget = item;
    showDeleteConfirm = true;
  }

  function cancelDelete() {
    showDeleteConfirm = false;
    deleteTarget = null;
  }

  async function confirmDelete() {
    if (!deleteTarget) return;

    isDeleting = true;
    await new Promise((resolve) => setTimeout(resolve, 300));

    therapists = therapists.filter((t) => t.id !== deleteTarget?.id);

    isDeleting = false;
    showDeleteConfirm = false;
    toast.success(`Removed ${deleteTarget.user.full_name} from therapist directory.`);
    deleteTarget = null;
  }

  function initials(name: string) {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? '')
      .join('');
  }

  function statusPillClass(status: TherapistStatus) {
    return status === 'active'
      ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
      : 'bg-slate-100 text-slate-700 border-slate-200';
  }
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
          Manage therapist accounts with backend-aligned RBAC defaults: <span class="font-medium">is_staff=true</span>,
          <span class="font-medium">is_superuser=false</span>.
        </p>
      </div>
      <Button class="bg-blue-600 text-white hover:bg-blue-700" onclick={openCreateDrawer}>
        + Add Therapist
      </Button>
    </div>
  </header>

  <div class="grid gap-4 sm:grid-cols-3">
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Total therapists</p>
      <p class="mt-2 text-2xl font-semibold text-blue-900">{therapists.length}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Active</p>
      <p class="mt-2 text-2xl font-semibold text-emerald-700">{activeCount}</p>
    </article>
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Inactive</p>
      <p class="mt-2 text-2xl font-semibold text-slate-700">{inactiveCount}</p>
    </article>
  </div>

  <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
    <div class="flex flex-wrap items-center gap-3">
      <div class="min-w-[240px] flex-1">
        <Input
          type="search"
          bind:value={searchQuery}
          className="h-11 border-blue-200"
          placeholder="Search by therapist name, email, or specialty"
        />
      </div>

      <div class="inline-flex rounded-lg border border-blue-200 bg-white p-1 text-sm">
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'all' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => (statusFilter = 'all')}
        >
          All
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'active' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => (statusFilter = 'active')}
        >
          Active
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'inactive' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => (statusFilter = 'inactive')}
        >
          Inactive
        </button>
      </div>
    </div>

    <div class="overflow-x-auto rounded-xl border border-slate-200">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
          <tr>
            <th class="px-4 py-3">Therapist</th>
            <th class="px-4 py-3">Email</th>
            <th class="px-4 py-3">Specialties</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          {#snippet therapistRow(item: TherapistAdminItem)}
            <tr class="hover:bg-blue-50/40">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="inline-flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                    {initials(item.user.full_name)}
                  </div>
                  <div>
                    <p class="font-medium text-slate-900">{item.user.full_name}</p>
                    <p class="text-xs text-slate-500">${item.profile.hourly_rate}/hr</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-700">{item.user.email}</td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-1.5">
                  {#each item.profile.specialties as spec (spec)}
                    <span class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                      {spec}
                    </span>
                  {/each}
                </div>
              </td>
              <td class="px-4 py-3">
                <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${statusPillClass(item.profile.status)}`}>
                  {item.profile.status}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <Button
                  type="button"
                  variant="outline"
                  class="border-rose-200 text-rose-700 hover:bg-rose-50"
                  onclick={() => requestDelete(item)}
                >
                  🗑 Delete
                </Button>
              </td>
            </tr>
          {/snippet}

          {#if filteredTherapists.length === 0}
            <tr>
              <td colspan="5" class="px-4 py-10 text-center text-slate-500">
                No therapists match your current filters.
              </td>
            </tr>
          {:else}
            {#each filteredTherapists as item (item.id)}
              {@render therapistRow(item)}
            {/each}
          {/if}
        </tbody>
      </table>
    </div>
  </section>

  {#if showCreateDrawer}
    <div class="fixed inset-0 z-50 flex">
      <button
        type="button"
        class="h-full w-full bg-black/40"
        onclick={closeCreateDrawer}
        aria-label="Close create therapist panel"
      ></button>

      <aside class="h-full w-full max-w-xl space-y-5 overflow-y-auto border-l border-blue-100 bg-white p-5 shadow-xl sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-blue-950">Create Therapist</h2>
            <p class="mt-1 text-sm text-slate-600">Creates both User and Therapist Profile in one action.</p>
          </div>
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeCreateDrawer}>✕</Button>
        </div>

        <div class="space-y-4">
          {#snippet field(label: string, required: boolean, description: string)}
            <div class="flex items-center justify-between">
              <Label class="font-medium text-slate-800">{label}{required ? ' *' : ''}</Label>
              <span class="text-xs text-slate-500">{description}</span>
            </div>
          {/snippet}

          <div class="space-y-2">
            {@render field('Full name', true, 'User data')}
            <Input bind:value={form.name} className="h-11 border-blue-200" placeholder="Dr. Alex Morgan" />
          </div>

          <div class="space-y-2">
            {@render field('Email', true, 'User data')}
            <Input type="email" bind:value={form.email} className="h-11 border-blue-200" placeholder="alex.morgan@therapy.local" />
          </div>

          <div class="space-y-2">
            {@render field('Password', true, 'User data')}
            <Input type="password" bind:value={form.password} className="h-11 border-blue-200" placeholder="••••••••" />
          </div>

          <div class="space-y-2">
            {@render field('Bio', false, 'Profile data')}
            <Textarea bind:value={form.bio} className="min-h-24 border-blue-200" placeholder="Short therapeutic approach and experience summary." />
          </div>

          <div class="space-y-2">
            {@render field('Specialties', true, 'Profile data')}
            <Input bind:value={form.specialties} className="h-11 border-blue-200" placeholder="Anxiety, CBT, Trauma" />
            <p class="text-xs text-slate-500">Use comma-separated values.</p>
          </div>

          <div class="space-y-2">
            {@render field('Hourly Rate (USD)', true, 'Profile data')}
            <Input type="number" bind:value={form.hourlyRate} className="h-11 border-blue-200" placeholder="110" min="1" step="1" />
          </div>
        </div>

        <div class="rounded-xl border border-blue-100 bg-blue-50 p-3 text-xs text-blue-800">
          <p class="font-semibold">RBAC payload defaults (mock):</p>
          <p class="mt-1">`is_staff: true` and `is_superuser: false` are always enforced for therapist creation.</p>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeCreateDrawer}>Cancel</Button>
          <Button type="button" class="bg-blue-600 text-white hover:bg-blue-700" onclick={createTherapist} disabled={isCreating}>
            {isCreating ? 'Creating…' : 'Create Therapist'}
          </Button>
        </div>
      </aside>
    </div>
  {/if}

  {#if showDeleteConfirm && deleteTarget}
    <div class="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <article class="w-full max-w-md space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
        <h3 class="text-lg font-semibold text-slate-900">Delete therapist?</h3>
        <p class="text-sm text-slate-600">
          This will remove <span class="font-medium">{deleteTarget.user.full_name}</span> from the therapist list.
          (Mock flow simulates deleting both linked user and therapist profile.)
        </p>

        <div class="flex justify-end gap-2">
          <Button type="button" variant="outline" class="border-slate-200" onclick={cancelDelete}>Keep therapist</Button>
          <Button type="button" class="bg-rose-600 text-white hover:bg-rose-700" onclick={confirmDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting…' : 'Delete'}
          </Button>
        </div>
      </article>
    </div>
  {/if}
</section>
