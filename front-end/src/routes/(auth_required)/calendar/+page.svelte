<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { ApiError, therapyApi } from '$lib/api';
  import { Button } from '$lib/components/ui/button';
  import type { Appointment, AppointmentStatus, AppointmentType } from '$lib/types';
  import { formatDateKey, formatDateTime, formatSessionType, formatTime } from '$lib/utils/therapy';

  type ViewMode = 'month' | 'week' | 'day';

  let sessions = $state<Appointment[]>([]);
  let mode = $state<ViewMode>('month');
  let activeStatus = $state<AppointmentStatus | 'all'>('all');
  let activeType = $state<AppointmentType | 'all'>('all');
  let focusedDate = $state(new Date());
  let isLoading = $state(true);
  let loadError = $state('');
  let actionInProgress = $state('');

  const monthLabelFormat = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric'
  });

  const dayTitleFormat = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  let focusedDateISO = $derived(formatDateKey(focusedDate));
  let monthLabel = $derived(monthLabelFormat.format(focusedDate));

  let filteredSessions = $derived(
    sessions
      .filter((session) => activeStatus === 'all' || session.status === activeStatus)
      .filter((session) => activeType === 'all' || session.appointment_type === activeType)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))
  );

  let sessionsByDay = $derived.by(() => {
    const map = new Map<string, Appointment[]>();
    for (const session of filteredSessions) {
      const day = formatDateKey(new Date(session.scheduled_at));
      if (!map.has(day)) map.set(day, []);
      map.get(day)?.push(session);
    }
    return map;
  });

  let monthGrid = $derived.by(() => {
    const start = new Date(focusedDate.getFullYear(), focusedDate.getMonth(), 1);
    const end = new Date(focusedDate.getFullYear(), focusedDate.getMonth() + 1, 0);
    const leading = start.getDay();
    const days = end.getDate();
    const total = Math.ceil((leading + days) / 7) * 7;
    const todayIso = formatDateKey(new Date());

    return Array.from({ length: total }, (_, i) => {
      const dayDate = new Date(focusedDate.getFullYear(), focusedDate.getMonth(), i - leading + 1);
      const iso = formatDateKey(dayDate);
      const daySessions = sessionsByDay.get(iso) ?? [];
      return {
        iso,
        dayNumber: dayDate.getDate(),
        inMonth: dayDate.getMonth() === focusedDate.getMonth(),
        isToday: iso === todayIso,
        total: daySessions.length,
        hasConfirmed: daySessions.some((session) => session.status === 'confirmed'),
        hasPending: daySessions.some((session) => session.status === 'pending')
      };
    });
  });

  let weekSessions = $derived.by(() => {
    const start = new Date(focusedDate);
    start.setDate(focusedDate.getDate() - focusedDate.getDay());

    return Array.from({ length: 7 }, (_, index) => {
      const day = new Date(start);
      day.setDate(start.getDate() + index);
      const iso = formatDateKey(day);
      return {
        iso,
        label: dayTitleFormat.format(day),
        sessions: sessionsByDay.get(iso) ?? []
      };
    });
  });

  let daySessions = $derived(sessionsByDay.get(focusedDateISO) ?? []);

  let nextSession = $derived(
    filteredSessions.find((session) => +new Date(session.scheduled_at) > Date.now()) ?? null
  );

  function getPatientName(session: Appointment) {
    return session.patient_name || session.patient_email || 'Patient';
  }

  function shiftDate(step: number) {
    const next = new Date(focusedDate);
    if (mode === 'month') {
      next.setMonth(focusedDate.getMonth() + step);
    } else if (mode === 'week') {
      next.setDate(focusedDate.getDate() + step * 7);
    } else {
      next.setDate(focusedDate.getDate() + step);
    }
    focusedDate = next;
  }

  function selectDay(iso: string) {
    focusedDate = new Date(`${iso}T00:00:00`);
    mode = 'day';
  }

  function statusClass(status: AppointmentStatus) {
    if (status === 'confirmed') return 'bg-emerald-100 text-emerald-700';
    if (status === 'pending') return 'bg-amber-100 text-amber-700';
    if (status === 'completed') return 'bg-blue-100 text-blue-700';
    if (status === 'no_show') return 'bg-slate-200 text-slate-700';
    return 'bg-rose-100 text-rose-700';
  }

  async function loadSessions() {
    isLoading = true;
    loadError = '';

    try {
      const response = await therapyApi.listAppointments(undefined, 'therapist');
      sessions = response.results;
    } catch (err) {
      loadError = err instanceof ApiError ? err.message : 'Failed to load therapist appointments.';
    } finally {
      isLoading = false;
    }
  }

  async function refreshSessions() {
    try {
      const response = await therapyApi.listAppointments(undefined, 'therapist');
      sessions = response.results;
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to refresh appointments.');
    }
  }

  async function confirmSession(id: string) {
    actionInProgress = `confirm:${id}`;

    try {
      await therapyApi.confirmAppointment(id);
      await refreshSessions();
      toast.success('Session confirmed.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to confirm session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function completeSession(id: string) {
    actionInProgress = `complete:${id}`;

    try {
      await therapyApi.completeAppointment(id);
      await refreshSessions();
      toast.success('Session marked complete.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to complete session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function cancelSession(id: string) {
    actionInProgress = `cancel:${id}`;

    try {
      await therapyApi.cancelAppointment(id, 'Cancelled by therapist');
      await refreshSessions();
      toast.success('Session cancelled.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to cancel session.');
    } finally {
      actionInProgress = '';
    }
  }

  async function generateMeetingLink(id: string) {
    actionInProgress = `meeting:${id}`;

    try {
      const response = await therapyApi.generateMeetingLink(id);
      sessions = sessions.map((session) =>
        session.id === id ? { ...session, meeting_link: response.meeting_link } : session
      );
      toast.success('Meeting link ready.');
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : 'Failed to generate meeting link.');
    } finally {
      actionInProgress = '';
    }
  }

  onMount(() => {
    void loadSessions();
  });
</script>

<svelte:head>
  <title>Therapist Calendar - Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <header class="rounded-lg border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm">
    <p class="text-xs font-semibold uppercase tracking-wide text-blue-500">Therapist Calendar</p>
    <h1 class="mt-2 text-2xl font-semibold text-blue-950 sm:text-3xl">Session Planning Workspace</h1>
    <p class="mt-1 text-sm text-slate-600">
      Real therapist appointments with confirm, cancel, complete, and meeting link actions.
    </p>
  </header>

  {#if isLoading}
    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-live="polite">
      {#each Array(6) as _, index (index)}
        <article class="h-32 animate-pulse rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <div class="h-4 w-32 rounded bg-blue-100"></div>
          <div class="mt-4 h-8 w-20 rounded bg-blue-50"></div>
        </article>
      {/each}
    </section>
  {:else if loadError}
    <section class="rounded-lg border border-rose-200 bg-rose-50 p-6">
      <h2 class="text-lg font-semibold text-rose-900">Unable to load calendar</h2>
      <p class="mt-2 text-sm text-rose-700">{loadError}</p>
      <Button class="mt-4 bg-blue-600 text-white hover:bg-blue-700" onclick={loadSessions}>Retry</Button>
    </section>
  {:else}
    <div class="grid gap-6 lg:grid-cols-[1.55fr_1fr]">
      <article class="space-y-4 rounded-lg border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <Button variant="outline" class="border-blue-200 text-blue-700" onclick={() => shiftDate(-1)}>
              Prev
            </Button>
            <h2 class="text-lg font-semibold text-blue-900">{monthLabel}</h2>
            <Button variant="outline" class="border-blue-200 text-blue-700" onclick={() => shiftDate(1)}>
              Next
            </Button>
          </div>

          <div class="flex items-center gap-2">
            <Button variant={mode === 'month' ? 'default' : 'outline'} onclick={() => (mode = 'month')}>Month</Button>
            <Button variant={mode === 'week' ? 'default' : 'outline'} onclick={() => (mode = 'week')}>Week</Button>
            <Button variant={mode === 'day' ? 'default' : 'outline'} onclick={() => (mode = 'day')}>Day</Button>
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <select bind:value={activeStatus} class="rounded-lg border border-blue-200 px-3 py-2 text-sm">
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="no_show">No show</option>
          </select>

          <select bind:value={activeType} class="rounded-lg border border-blue-200 px-3 py-2 text-sm">
            <option value="all">All session types</option>
            <option value="video">Video</option>
            <option value="in_person">In person</option>
            <option value="phone">Phone</option>
          </select>

          <Button variant="outline" class="border-blue-200 text-blue-700" onclick={refreshSessions}>
            Refresh
          </Button>
        </div>

        {#if mode === 'month'}
          <div class="grid grid-cols-7 gap-2 text-center text-xs font-semibold uppercase tracking-wide text-blue-500">
            <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
          </div>

          <div class="grid grid-cols-7 gap-2">
            {#each monthGrid as day (day.iso)}
              <button
                type="button"
                class={`relative min-h-20 rounded-lg border p-2 text-left text-sm transition ${
                  day.inMonth ? 'border-blue-100 bg-white hover:bg-blue-50' : 'border-transparent bg-blue-50/40 text-blue-300'
                } ${focusedDateISO === day.iso ? 'border-blue-500 ring-2 ring-blue-200' : ''}`}
                onclick={() => selectDay(day.iso)}
                disabled={!day.inMonth}
              >
                <p class="font-medium">{day.dayNumber}</p>
                {#if day.total > 0}
                  <p class="mt-2 text-xs text-slate-600">{day.total} session{day.total > 1 ? 's' : ''}</p>
                  <div class="mt-1 flex gap-1">
                    {#if day.hasConfirmed}
                      <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    {/if}
                    {#if day.hasPending}
                      <span class="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
                    {/if}
                  </div>
                {/if}
                {#if day.isToday}
                  <span class="absolute right-2 top-2 rounded-full bg-blue-100 px-1.5 text-[10px] font-semibold text-blue-700">Today</span>
                {/if}
              </button>
            {/each}
          </div>
        {:else if mode === 'week'}
          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {#each weekSessions as day (day.iso)}
              <article class="rounded-lg border border-blue-100 p-3">
                <h3 class="font-medium text-blue-900">{day.label}</h3>
                {#if day.sessions.length === 0}
                  <p class="mt-2 text-sm text-slate-500">No sessions</p>
                {:else}
                  <ul class="mt-2 space-y-2 text-sm">
                    {#each day.sessions as session (session.id)}
                      <li class="rounded-lg bg-blue-50 px-2 py-1.5">
                        <p class="font-medium text-blue-900">{formatTime(session.scheduled_at)} - {getPatientName(session)}</p>
                        <p class="text-slate-600">{formatSessionType(session.appointment_type)}</p>
                      </li>
                    {/each}
                  </ul>
                {/if}
              </article>
            {/each}
          </div>
        {:else}
          <article class="space-y-3 rounded-lg border border-blue-100 p-4">
            <h3 class="font-medium text-blue-900">
              {new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).format(focusedDate)}
            </h3>
            {#if daySessions.length === 0}
              <p class="text-sm text-slate-500">No sessions scheduled for this day.</p>
            {:else}
              <ul class="space-y-2">
                {#each daySessions as session (session.id)}
                  <li class="rounded-lg bg-blue-50 px-3 py-2 text-sm text-slate-700">
                    <p class="font-medium text-blue-900">{formatTime(session.scheduled_at)} - {getPatientName(session)}</p>
                    <p>{session.duration_minutes} min / {formatSessionType(session.appointment_type)}</p>
                  </li>
                {/each}
              </ul>
            {/if}
          </article>
        {/if}
      </article>

      <aside class="space-y-4">
        <article class="rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <h3 class="text-sm font-semibold text-blue-900">Next Session</h3>
          {#if nextSession}
            <p class="mt-2 text-sm font-medium text-blue-900">{getPatientName(nextSession)}</p>
            <p class="text-sm text-slate-700">{formatDateTime(nextSession.scheduled_at)}</p>
            {#if nextSession.reason}
              <p class="mt-1 text-xs text-slate-500">{nextSession.reason}</p>
            {/if}
          {:else}
            <p class="mt-2 text-sm text-slate-500">No upcoming sessions for selected filters.</p>
          {/if}
        </article>

        <article class="space-y-3 rounded-lg border border-blue-100 bg-white p-4 shadow-sm">
          <h3 class="text-sm font-semibold text-blue-900">Session Queue</h3>
          {#if filteredSessions.length === 0}
            <p class="text-sm text-slate-500">No sessions available.</p>
          {:else}
            {#each filteredSessions.slice(0, 8) as session (session.id)}
              <div class="rounded-lg border border-slate-200 p-3">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p class="font-medium text-blue-900">{getPatientName(session)}</p>
                    <p class="text-xs text-slate-600">{formatDateTime(session.scheduled_at)}</p>
                  </div>
                  <span class={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${statusClass(session.status)}`}>
                    {session.status}
                  </span>
                </div>

                {#if session.reason}
                  <p class="mt-2 text-xs text-slate-600">{session.reason}</p>
                {/if}

                <div class="mt-3 flex flex-wrap gap-2">
                  {#if session.status === 'pending'}
                    <Button
                      class="bg-blue-600 text-white hover:bg-blue-700"
                      onclick={() => confirmSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `confirm:${session.id}` ? 'Confirming...' : 'Confirm'}
                    </Button>
                  {/if}

                  {#if session.status === 'confirmed'}
                    <Button
                      variant="outline"
                      class="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                      onclick={() => completeSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `complete:${session.id}` ? 'Saving...' : 'Complete'}
                    </Button>
                    <Button
                      variant="outline"
                      class="border-rose-300 text-rose-700 hover:bg-rose-50"
                      onclick={() => cancelSession(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `cancel:${session.id}` ? 'Cancelling...' : 'Cancel'}
                    </Button>
                    <Button
                      variant="outline"
                      class="border-blue-300 text-blue-700 hover:bg-blue-50"
                      onclick={() => generateMeetingLink(session.id)}
                      disabled={Boolean(actionInProgress)}
                    >
                      {actionInProgress === `meeting:${session.id}` ? 'Preparing...' : session.meeting_link ? 'Refresh link' : 'Generate link'}
                    </Button>
                  {/if}

                  {#if session.meeting_link}
                    <a href={session.meeting_link} target="_blank" rel="noreferrer" class="inline-flex">
                      <Button variant="outline" class="border-blue-200 text-blue-700 hover:bg-blue-50">Open link</Button>
                    </a>
                  {/if}
                </div>
              </div>
            {/each}
          {/if}
        </article>
      </aside>
    </div>
  {/if}
</section>
