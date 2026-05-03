<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';

  // ========== TYPES ==========
  type AppointmentStatus = 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  type AppointmentType = 'individual' | 'couples' | 'family' | 'consultation';

  interface Appointment {
    id: string;
    patient: {
      id: string;
      name: string;
      email: string;
    };
    therapist: {
      id: string;
      name: string;
      email: string;
    };
    status: AppointmentStatus;
    type: AppointmentType;
    scheduled_time: string;
    duration_minutes: number;
    notes?: string;
    created_at: string;
    updated_at: string;
  }

  interface ApiResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Appointment[];
  }

  // ========== STATE ==========
  let appointments = $state<Appointment[]>([]);
  let searchQuery = $state('');
  let statusFilter = $state<AppointmentStatus | 'all'>('all');
  let therapistFilter = $state<string>('all');
  let dateRangeStart = $state<string>('');
  let dateRangeEnd = $state<string>('');
  
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  
  // Pagination
  let currentPage = $state(1);
  let totalPages = $state(1);
  let totalAppointments = $state(0);
  let pageSize = $state(25);
  
  let showDetailsModal = $state(false);
  let selectedAppointment = $state<Appointment | null>(null);
  let isUpdating = $state(false);

  // Debounced search
  let debounceTimer: NodeJS.Timeout;

  // Get unique therapists for filter
  let therapists = $derived(() => {
    const unique = new Map();
    appointments.forEach(apt => {
      if (!unique.has(apt.therapist.id)) {
        unique.set(apt.therapist.id, apt.therapist);
      }
    });
    return Array.from(unique.values());
  });

  // Stats
  let scheduledCount = $derived(appointments.filter(a => a.status === 'scheduled').length);
  let confirmedCount = $derived(appointments.filter(a => a.status === 'confirmed').length);
  let completedCount = $derived(appointments.filter(a => a.status === 'completed').length);
  let cancelledCount = $derived(appointments.filter(a => a.status === 'cancelled').length);
  let noShowCount = $derived(appointments.filter(a => a.status === 'no_show').length);

  // ========== API CALLS ==========
  
  // Load appointments from API
  async function loadAppointments() {
    isLoading = true;
    error = null;
    
    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', pageSize.toString());
      
      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }
      
      if (therapistFilter !== 'all') {
        params.append('therapist_id', therapistFilter);
      }
      
      if (dateRangeStart) {
        params.append('start_date', dateRangeStart);
      }
      
      if (dateRangeEnd) {
        params.append('end_date', dateRangeEnd);
      }
      
      const response = await fetch(`/api/v1/admin/appointments/?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load appointments: ${response.status}`);
      }
      
      const data: ApiResponse = await response.json();
      appointments = data.results;
      totalAppointments = data.count;
      totalPages = Math.ceil(data.count / pageSize);
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load appointments';
      toast.error(error);
    } finally {
      isLoading = false;
    }
  }
  
  // Update appointment status (admin override)
  async function updateAppointmentStatus(appointment: Appointment, newStatus: AppointmentStatus) {
    const actionMap: Record<string, string> = {
      confirmed: 'force confirm',
      cancelled: 'force cancel',
      no_show: 'mark as no-show'
    };
    
    const actionText = actionMap[newStatus] || newStatus;
    const confirmed = confirm(`Are you sure you want to ${actionText} this appointment for ${appointment.patient.name}?`);
    
    if (!confirmed) return;
    
    isUpdating = true;
    
    // Optimistic update
    const originalAppointments = [...appointments];
    appointments = appointments.map(a => 
      a.id === appointment.id ? { ...a, status: newStatus, updated_at: new Date().toISOString() } : a
    );
    
    try {
      const response = await fetch(`/api/v1/admin/appointments/${appointment.id}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to ${actionText} appointment`);
      }
      
      const updatedAppointment = await response.json();
      
      // Update with actual server response
      appointments = appointments.map(a => 
        a.id === appointment.id ? updatedAppointment : a
      );
      
      toast.success(`Appointment ${actionText}ed successfully for ${appointment.patient.name}`);
    } catch (err) {
      // Revert optimistic update
      appointments = originalAppointments;
      toast.error(err instanceof Error ? err.message : `Failed to ${actionText} appointment`);
    } finally {
      isUpdating = false;
    }
  }
  
  // Debounced search
  function onSearchInput(value: string) {
    searchQuery = value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentPage = 1;
      loadAppointments();
    }, 300);
  }
  
  // Handle filter changes
  function changeStatusFilter(filter: typeof statusFilter) {
    statusFilter = filter;
    currentPage = 1;
    loadAppointments();
  }
  
  function changeTherapistFilter(filter: string) {
    therapistFilter = filter;
    currentPage = 1;
    loadAppointments();
  }
  
  function changeDateRange() {
    currentPage = 1;
    loadAppointments();
  }
  
  function goToPage(page: number) {
    currentPage = page;
    loadAppointments();
  }
  
  function resetFilters() {
    searchQuery = '';
    statusFilter = 'all';
    therapistFilter = 'all';
    dateRangeStart = '';
    dateRangeEnd = '';
    currentPage = 1;
    loadAppointments();
  }
  
  // Open details modal
  function openAppointmentDetails(appointment: Appointment) {
    selectedAppointment = appointment;
    showDetailsModal = true;
  }
  
  function closeDetailsModal() {
    showDetailsModal = false;
    selectedAppointment = null;
  }
  
  // ========== CSV EXPORT ==========
  async function exportToCSV() {
    try {
      // Fetch all appointments without pagination for export
      const params = new URLSearchParams();
      params.append('page_size', '1000'); // Get max records
      
      if (searchQuery.trim()) params.append('search', searchQuery.trim());
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (therapistFilter !== 'all') params.append('therapist_id', therapistFilter);
      if (dateRangeStart) params.append('start_date', dateRangeStart);
      if (dateRangeEnd) params.append('end_date', dateRangeEnd);
      
      const response = await fetch(`/api/v1/admin/appointments/?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch data for export');
      
      const data: ApiResponse = await response.json();
      const exportData = data.results;
      
      const headers = ['Patient', 'Patient Email', 'Therapist', 'Therapist Email', 'Status', 'Type', 'Scheduled Time', 'Duration (min)', 'Notes'];
      
      const rows = exportData.map(a => [
        a.patient.name,
        a.patient.email,
        a.therapist.name,
        a.therapist.email,
        a.status.replace('_', ' ').toUpperCase(),
        a.type,
        formatDateTime(a.scheduled_time),
        a.duration_minutes.toString(),
        a.notes || ''
      ]);
      
      const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `appointments_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      
      toast.success(`Exported ${exportData.length} appointments to CSV`);
    } catch (err) {
      toast.error('Failed to export appointments');
    }
  }
  
  // ========== HELPER FUNCTIONS ==========
  function formatDateTime(dateString: string) {
    return new Date(dateString).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  }
  
  function getStatusColor(status: AppointmentStatus) {
    switch(status) {
      case 'scheduled': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'confirmed': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'completed': return 'bg-green-100 text-green-700 border-green-200';
      case 'cancelled': return 'bg-red-100 text-red-700 border-red-200';
      case 'no_show': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  }
  
  function getTypeIcon(type: AppointmentType) {
    switch(type) {
      case 'individual': return 'fa-user';
      case 'couples': return 'fa-heart';
      case 'family': return 'fa-users';
      case 'consultation': return 'fa-stethoscope';
      default: return 'fa-calendar';
    }
  }
  
  // Load on mount
  onMount(() => {
    loadAppointments();
  });
</script>

<svelte:head>
  <title>Admin • Appointment Operations — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <!-- Header -->
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
    <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Admin Console</p>
        <h1 class="mt-2 text-2xl font-semibold text-blue-950 sm:text-3xl">Appointment Operations</h1>
        <p class="mt-1 text-sm text-slate-600">
          Monitor and manage all appointments across the platform. Admin overrides available.
        </p>
      </div>
      <Button onclick={exportToCSV} class="bg-emerald-600 text-white hover:bg-emerald-700">
        📥 Export to CSV
      </Button>
    </div>
  </header>

  <!-- Stats Cards -->
  {#if !isLoading && !error}
    <div class="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Total</p>
        <p class="mt-2 text-2xl font-semibold text-blue-900">{totalAppointments}</p>
      </article>
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Scheduled</p>
        <p class="mt-2 text-2xl font-semibold text-blue-600">{scheduledCount}</p>
      </article>
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Confirmed</p>
        <p class="mt-2 text-2xl font-semibold text-emerald-600">{confirmedCount}</p>
      </article>
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Completed</p>
        <p class="mt-2 text-2xl font-semibold text-green-600">{completedCount}</p>
      </article>
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">Cancelled</p>
        <p class="mt-2 text-2xl font-semibold text-red-600">{cancelledCount}</p>
      </article>
      <article class="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
        <p class="text-xs uppercase tracking-wide text-blue-500">No Show</p>
        <p class="mt-2 text-2xl font-semibold text-gray-600">{noShowCount}</p>
      </article>
    </div>
  {/if}

  <!-- Filters & Table -->
  <section class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
    <!-- Filter Bar -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="min-w-[200px] flex-1">
        <Input
          type="search"
          placeholder="Search by patient or therapist..."
          class="h-11 border-blue-200"
          value={searchQuery}
          oninput={(e) => onSearchInput(e.currentTarget.value)}
        />
      </div>
      
      <select
        bind:value={statusFilter}
        onchange={() => changeStatusFilter(statusFilter)}
        class="h-11 rounded-lg border border-blue-200 bg-white px-3 text-sm"
      >
        <option value="all">All Statuses</option>
        <option value="scheduled">Scheduled</option>
        <option value="confirmed">Confirmed</option>
        <option value="completed">Completed</option>
        <option value="cancelled">Cancelled</option>
        <option value="no_show">No Show</option>
      </select>
      
      <select
        bind:value={therapistFilter}
        onchange={() => changeTherapistFilter(therapistFilter)}
        class="h-11 rounded-lg border border-blue-200 bg-white px-3 text-sm"
      >
        <option value="all">All Therapists</option>
        {#each therapists() as therapist}
          <option value={therapist.id}>{therapist.name}</option>
        {/each}
      </select>
      
      <input
        type="date"
        bind:value={dateRangeStart}
        onchange={changeDateRange}
        class="h-11 rounded-lg border border-blue-200 bg-white px-3 text-sm"
        placeholder="Start Date"
      />
      
      <input
        type="date"
        bind:value={dateRangeEnd}
        onchange={changeDateRange}
        class="h-11 rounded-lg border border-blue-200 bg-white px-3 text-sm"
        placeholder="End Date"
      />
      
      <Button onclick={resetFilters} variant="outline" class="border-slate-200">
        Reset Filters
      </Button>
    </div>

    <!-- Loading/Error States -->
    {#if isLoading}
      <div class="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p class="text-slate-600">Loading appointments...</p>
      </div>
    {:else if error}
      <div class="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
        <p class="text-red-600">Error: {error}</p>
        <Button onclick={() => loadAppointments()} class="mt-4">Retry</Button>
      </div>
    {:else}
      <!-- Appointments Table -->
      <div class="overflow-x-auto rounded-xl border border-slate-200">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
            <tr>
              <th class="px-4 py-3">Patient</th>
              <th class="px-4 py-3">Therapist</th>
              <th class="px-4 py-3">Type</th>
              <th class="px-4 py-3">Scheduled Time</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            {#each appointments as apt (apt.id)}
              <tr 
                class="cursor-pointer hover:bg-blue-50/40 transition"
                onclick={() => openAppointmentDetails(apt)}
              >
                <td class="px-4 py-3">
                  <div>
                    <p class="font-medium text-slate-900">{apt.patient.name}</p>
                    <p class="text-xs text-slate-500">{apt.patient.email}</p>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="font-medium text-slate-900">{apt.therapist.name}</p>
                  <p class="text-xs text-slate-500">{apt.therapist.email}</p>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <i class={`fa-solid ${getTypeIcon(apt.type)} text-blue-500`}></i>
                    <span class="capitalize">{apt.type}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div>
                    <p class="font-medium text-slate-900">{formatDateTime(apt.scheduled_time)}</p>
                    <p class="text-xs text-slate-500">{apt.duration_minutes} min</p>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusColor(apt.status)}`}>
                    {apt.status.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex justify-end gap-2">
                    {#if apt.status !== 'confirmed' && apt.status !== 'completed'}
                      <Button
                        type="button"
                        size="sm"
                        class="bg-emerald-600 text-white hover:bg-emerald-700"
                        onclick={(e) => {
                          e.stopPropagation();
                          updateAppointmentStatus(apt, 'confirmed');
                        }}
                        disabled={isUpdating}
                      >
                        ✓ Confirm
                      </Button>
                    {/if}
                    
                    {#if apt.status !== 'cancelled' && apt.status !== 'completed'}
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        class="border-red-200 text-red-700 hover:bg-red-50"
                        onclick={(e) => {
                          e.stopPropagation();
                          updateAppointmentStatus(apt, 'cancelled');
                        }}
                        disabled={isUpdating}
                      >
                        ✗ Cancel
                      </Button>
                    {/if}
                    
                    {#if apt.status !== 'no_show' && apt.status !== 'completed'}
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        class="border-gray-200 text-gray-700 hover:bg-gray-50"
                        onclick={(e) => {
                          e.stopPropagation();
                          updateAppointmentStatus(apt, 'no_show');
                        }}
                        disabled={isUpdating}
                      >
                        ⚠ No Show
                      </Button>
                    {/if}
                  </div>
                </td>
              </tr>
            {/each}

            {#if appointments.length === 0}
              <tr>
                <td colspan="6" class="px-4 py-10 text-center text-slate-500">
                  No appointments match your current filters.
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
            Page {currentPage} of {totalPages} ({totalAppointments} total appointments)
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

  <!-- Appointment Details Modal -->
  {#if showDetailsModal && selectedAppointment}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <article class="w-full max-w-2xl space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
        <div class="flex items-start justify-between">
          <h2 class="text-xl font-semibold text-slate-900">Appointment Details</h2>
          <Button type="button" variant="outline" class="border-slate-200" onclick={closeDetailsModal}>✕</Button>
        </div>
        
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Patient</p>
            <p class="font-medium text-slate-900">{selectedAppointment.patient.name}</p>
            <p class="text-sm text-slate-600">{selectedAppointment.patient.email}</p>
          </div>
          
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Therapist</p>
            <p class="font-medium text-slate-900">{selectedAppointment.therapist.name}</p>
            <p class="text-sm text-slate-600">{selectedAppointment.therapist.email}</p>
          </div>
          
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Appointment Type</p>
            <p class="capitalize text-slate-900">{selectedAppointment.type}</p>
          </div>
          
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Duration</p>
            <p class="text-slate-900">{selectedAppointment.duration_minutes} minutes</p>
          </div>
          
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Scheduled Time</p>
            <p class="text-slate-900">{formatDateTime(selectedAppointment.scheduled_time)}</p>
          </div>
          
          <div class="space-y-2">
            <p class="text-xs font-semibold uppercase text-slate-500">Status</p>
            <span class={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${getStatusColor(selectedAppointment.status)}`}>
              {selectedAppointment.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          
          {#if selectedAppointment.notes}
            <div class="sm:col-span-2 space-y-2">
              <p class="text-xs font-semibold uppercase text-slate-500">Notes</p>
              <p class="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{selectedAppointment.notes}</p>
            </div>
          {/if}
        </div>
        
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-200">
          <Button variant="outline" class="border-slate-200" onclick={closeDetailsModal}>Close</Button>
        </div>
      </article>
    </div>
  {/if}
</section>