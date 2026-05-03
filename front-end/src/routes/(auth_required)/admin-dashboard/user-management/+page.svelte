<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  
  // Types based on API response
  interface User {
    id: string;
    email: string;
    full_name: string;
    user_type: 'patient' | 'therapist' | 'admin';
    is_active: boolean;
    date_joined: string;
    last_login: string;
    appointments_count?: number;
    profile?: {
      first_name: string;
      last_name: string;
      phone_number?: string;
    };
  }

  interface PaginatedResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: User[];
  }

  // State
  let users = $state<User[]>([]);
  let searchQuery = $state('');
  let statusFilter = $state<'all' | 'active' | 'inactive'>('all');
  let userTypeFilter = $state<'all' | 'patient' | 'therapist'>('all');
  
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  
  // Pagination
  let currentPage = $state(1);
  let totalPages = $state(1);
  let totalUsers = $state(0);
  let pageSize = $state(25);
  
  let showDetailDrawer = $state(false);
  let selectedUser = $state<User | null>(null);
  let isUpdating = $state(false);

  // Debounced search
  let debounceTimer: NodeJS.Timeout;
  
  // Stats
  let activeCount = $derived(users.filter(u => u.is_active).length);
  let inactiveCount = $derived(users.filter(u => !u.is_active).length);

  // Load users from API
  async function loadUsers() {
    isLoading = true;
    error = null;
    
    try {
      // Build URL with all filters
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', pageSize.toString());
      
      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      
      if (statusFilter !== 'all') {
        params.append('is_active', statusFilter === 'active' ? 'true' : 'false');
      }
      
      if (userTypeFilter !== 'all') {
        params.append('user_type', userTypeFilter);
      }
      
      const url = `/api/v1/admin/users/?${params.toString()}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to load users: ${response.status}`);
      }
      
      const data: PaginatedResponse = await response.json();
      users = data.results;
      totalUsers = data.count;
      totalPages = Math.ceil(data.count / pageSize);
      
      // Update URL params without refreshing
      const urlParams = new URLSearchParams(window.location.search);
      if (searchQuery) urlParams.set('search', searchQuery);
      else urlParams.delete('search');
      if (statusFilter !== 'all') urlParams.set('status', statusFilter);
      else urlParams.delete('status');
      if (userTypeFilter !== 'all') urlParams.set('user_type', userTypeFilter);
      else urlParams.delete('user_type');
      urlParams.set('page', currentPage.toString());
      
      const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
      window.history.pushState({}, '', newUrl);
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load users';
      toast.error(error);
    } finally {
      isLoading = false;
    }
  }

  // Debounced search
  function onSearchInput(value: string) {
    searchQuery = value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentPage = 1;
      loadUsers();
    }, 300);
  }

  // Handle filter changes
  function changeStatusFilter(filter: typeof statusFilter) {
    statusFilter = filter;
    currentPage = 1;
    loadUsers();
  }
  
  function changeUserTypeFilter(filter: typeof userTypeFilter) {
    userTypeFilter = filter;
    currentPage = 1;
    loadUsers();
  }
  
  function goToPage(page: number) {
    currentPage = page;
    loadUsers();
  }

  // Toggle user status (activate/deactivate)
  async function toggleUserStatus(user: User) {
    const newStatus = !user.is_active;
    const action = newStatus ? 'activate' : 'deactivate';
    
    const confirmed = confirm(`Are you sure you want to ${action} ${user.full_name || user.email}?`);
    if (!confirmed) return;
    
    isUpdating = true;
    
    // Optimistic update
    const originalUsers = [...users];
    users = users.map(u => 
      u.id === user.id ? { ...u, is_active: newStatus } : u
    );
    
    try {
      const response = await fetch(`/api/v1/admin/users/${user.id}/${action}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to ${action} user`);
      }
      
      toast.success(`${user.full_name || user.email} has been ${action}d successfully.`);
      
      // Refresh to get updated data
      await loadUsers();
      
    } catch (err) {
      // Revert optimistic update
      users = originalUsers;
      toast.error(err instanceof Error ? err.message : `Failed to ${action} user`);
    } finally {
      isUpdating = false;
    }
  }

  // Open user details drawer
  function openUserDetails(user: User) {
    selectedUser = user;
    showDetailDrawer = true;
  }

  function closeUserDetails() {
    showDetailDrawer = false;
    selectedUser = null;
  }

  // Helper functions
  function formatDate(dateString: string) {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
  
  function formatLastLogin(dateString: string) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return formatDate(dateString);
  }

  function getUserTypeIcon(userType: string) {
    switch(userType) {
      case 'therapist': return 'fa-user-md';
      case 'admin': return 'fa-user-shield';
      default: return 'fa-user';
    }
  }

  function getUserTypeColor(userType: string) {
    switch(userType) {
      case 'therapist': return 'bg-purple-100 text-purple-700';
      case 'admin': return 'bg-red-100 text-red-700';
      default: return 'bg-blue-100 text-blue-700';
    }
  }
</script>

<svelte:head>
  <title>Admin • User Management — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <!-- Header -->
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Admin Console</p>
    <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-blue-950 sm:text-3xl">User Management</h1>
        <p class="mt-1 text-sm text-slate-600">
          Manage user accounts, activation status, and monitor user activity.
        </p>
      </div>
    </div>
  </header>

  <!-- Stats Cards -->
  <div class="grid gap-4 sm:grid-cols-3">
    <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
      <p class="text-xs uppercase tracking-wide text-blue-500">Total Users</p>
      <p class="mt-2 text-2xl font-semibold text-blue-900">{totalUsers}</p>
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

  <!-- Filters & Table -->
  <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
    <!-- Filter Bar -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="min-w-[240px] flex-1">
        <Input
          type="search"
          placeholder="Search by name or email..."
          class="h-11 border-blue-200"
          value={searchQuery}
          oninput={(e: Event) => onSearchInput((e.currentTarget as HTMLInputElement).value)}
        />
      </div>

      <div class="inline-flex rounded-lg border border-blue-200 bg-white p-1 text-sm">
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'all' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeStatusFilter('all')}
        >
          All Status
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'active' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeStatusFilter('active')}
        >
          Active
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${statusFilter === 'inactive' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeStatusFilter('inactive')}
        >
          Inactive
        </button>
      </div>

      <div class="inline-flex rounded-lg border border-blue-200 bg-white p-1 text-sm">
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${userTypeFilter === 'all' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeUserTypeFilter('all')}
        >
          All Types
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${userTypeFilter === 'patient' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeUserTypeFilter('patient')}
        >
          Patients
        </button>
        <button
          type="button"
          class={`rounded-md px-3 py-1.5 transition ${userTypeFilter === 'therapist' ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-blue-50'}`}
          onclick={() => changeUserTypeFilter('therapist')}
        >
          Therapists
        </button>
      </div>
    </div>

    <!-- Loading/Error States -->
    {#if isLoading}
      <div class="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p class="text-slate-600">Loading users...</p>
      </div>
    {:else if error}
      <div class="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
        <p class="text-red-600">Error: {error}</p>
        <Button onclick={() => loadUsers()} class="mt-4">Retry</Button>
      </div>
    {:else}
      <!-- Users Table -->
      <div class="overflow-x-auto rounded-xl border border-slate-200">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
            <tr>
              <th class="px-4 py-3">User</th>
              <th class="px-4 py-3">Email</th>
              <th class="px-4 py-3">Type</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Joined</th>
              <th class="px-4 py-3">Last Login</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            {#each users as user (user.id)}
              <tr 
                class="cursor-pointer hover:bg-blue-50/40 transition"
                onclick={() => openUserDetails(user)}
              >
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="inline-flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-blue-700">
                      <i class={`fa-solid ${getUserTypeIcon(user.user_type)}`}></i>
                    </div>
                    <div>
                      <p class="font-medium text-slate-900">{user.full_name || user.email.split('@')[0]}</p>
                      <p class="text-xs text-slate-500">{user.appointments_count || 0} appointments</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-slate-700">{user.email}</td>
                <td class="px-4 py-3">
                  <span class={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getUserTypeColor(user.user_type)}`}>
                    {user.user_type}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${
                    user.is_active 
                      ? 'bg-emerald-100 text-emerald-700 border-emerald-200' 
                      : 'bg-slate-100 text-slate-700 border-slate-200'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td class="px-4 py-3 text-slate-600">{formatDate(user.date_joined)}</td>
                <td class="px-4 py-3 text-slate-600">{formatLastLogin(user.last_login)}</td>
                <td class="px-4 py-3 text-right">
                  <Button
                    type="button"
                    variant="outline"
                    class={`${user.is_active ? 'border-amber-200 text-amber-700 hover:bg-amber-50' : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'}`}
                    onclick={(e: Event) => {
                      e.stopPropagation();
                      toggleUserStatus(user);
                    }}
                    disabled={isUpdating}
                  >
                    {user.is_active ? '🔒 Deactivate' : '✓ Activate'}
                  </Button>
                </td>
              </tr>
            {/each}

            {#if users.length === 0}
              <tr>
                <td colspan="7" class="px-4 py-10 text-center text-slate-500">
                  No users match your current filters.
                </td>
              </tr>
            {/if}
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      {#if totalPages > 1}
        <div class="flex items-center justify-between border-t border-slate-200 pt-4">
          <div class="text-sm text-slate-600">
            Page {currentPage} of {totalPages} ({totalUsers} total users)
          </div>
          <div class="flex gap-2">
            <Button 
              onclick={() => goToPage(currentPage - 1)} 
              disabled={currentPage === 1}
              variant="outline"
            >
              Previous
            </Button>
            <Button 
              onclick={() => goToPage(currentPage + 1)} 
              disabled={currentPage === totalPages}
              variant="outline"
            >
              Next
            </Button>
          </div>
        </div>
      {/if}
    {/if}
  </section>

  <!-- User Details Drawer -->
  {#if showDetailDrawer && selectedUser}
    <div class="fixed inset-0 z-50 flex">
      <button
        type="button"
        class="h-full w-full bg-black/40"
        onclick={closeUserDetails}
        aria-label="Close details panel"
      ></button>

      <aside class="h-full w-full max-w-md space-y-5 overflow-y-auto border-l border-blue-100 bg-white p-6 shadow-xl">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold text-blue-950">User Details</h2>
            <p class="mt-1 text-sm text-slate-600">View and manage user information</p>
          </div>
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeUserDetails}>✕</Button>
        </div>

        <div class="flex flex-col items-center text-center">
          <div class="inline-flex h-20 w-20 items-center justify-center rounded-full bg-blue-100 text-3xl text-blue-700">
            <i class={`fa-solid ${getUserTypeIcon(selectedUser.user_type)}`}></i>
          </div>
          <h3 class="mt-3 text-lg font-semibold text-slate-900">{selectedUser.full_name || selectedUser.email.split('@')[0]}</h3>
          <p class="text-sm text-slate-500">{selectedUser.email}</p>
        </div>

        <div class="space-y-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
          <div class="flex justify-between">
            <span class="text-sm text-slate-600">User Type:</span>
            <span class={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${getUserTypeColor(selectedUser.user_type)}`}>
              {selectedUser.user_type}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-slate-600">Status:</span>
            <span class={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
              selectedUser.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'
            }`}>
              {selectedUser.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-slate-600">Member since:</span>
            <span class="text-sm font-medium text-slate-900">{formatDate(selectedUser.date_joined)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-slate-600">Last login:</span>
            <span class="text-sm font-medium text-slate-900">{formatLastLogin(selectedUser.last_login)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-slate-600">Total appointments:</span>
            <span class="text-sm font-medium text-slate-900">{selectedUser.appointments_count || 0}</span>
          </div>
          {#if selectedUser.profile?.phone_number}
            <div class="flex justify-between">
              <span class="text-sm text-slate-600">Phone:</span>
              <span class="text-sm font-medium text-slate-900">{selectedUser.profile.phone_number}</span>
            </div>
          {/if}
        </div>

        <div class="space-y-2 pt-2">
          <Button 
            class={`w-full ${selectedUser.is_active ? 'bg-amber-600 hover:bg-amber-700' : 'bg-emerald-600 hover:bg-emerald-700'} text-white`}
            onclick={() => {
              if (!selectedUser) return;
              toggleUserStatus(selectedUser);
              closeUserDetails();
            }}
          >
            {selectedUser.is_active ? '🔒 Deactivate User' : '✓ Activate User'}
          </Button>
          <Button variant="outline" class="w-full border-slate-200" onclick={closeUserDetails}>
            Close
          </Button>
        </div>
      </aside>
    </div>
  {/if}
</section>
