<script lang="ts">
  import { Button } from '$lib/components/ui/button';

  type ViewMode = 'month' | 'week' | 'day';
  type SessionStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled';
  type SessionType = 'video' | 'in_person' | 'phone';

  interface CalendarSession {
    id: string;
    patient_name: string;
    status: SessionStatus;
    appointment_type: SessionType;
    scheduled_at: string;
    duration_minutes: number;
    reason: string;
    meeting_link?: string | null;
  }

  const base = new Date();

  const mockSessionsSeed: CalendarSession[] = [
    {
      id: 's-1',
      patient_name: 'Amara Kent',
      status: 'confirmed',
      appointment_type: 'video',
      scheduled_at: new Date(base.getFullYear(), base.getMonth(), base.getDate(), 9, 0).toISOString(),
      duration_minutes: 50,
      reason: 'Anxiety coping tools and stress cycles',
      meeting_link: null
    },
    {
      id: 's-2',
      patient_name: 'Jonah Lee',
      status: 'pending',
      appointment_type: 'in_person',
      scheduled_at: new Date(base.getFullYear(), base.getMonth(), base.getDate() + 1, 11, 0).toISOString(),
      duration_minutes: 50,
      reason: 'Relationship boundary coaching',
      meeting_link: null
    },
    {
      id: 's-3',
      patient_name: 'Nina Brooks',
      status: 'confirmed',
      appointment_type: 'phone',
      scheduled_at: new Date(base.getFullYear(), base.getMonth(), base.getDate() + 2, 14, 30).toISOString(),
      duration_minutes: 30,
      reason: 'Medication side-effect check-in',
      meeting_link: null
    },
    {
      id: 's-4',
      patient_name: 'Daniel Moss',
      status: 'completed',
      appointment_type: 'video',
      scheduled_at: new Date(base.getFullYear(), base.getMonth(), base.getDate() - 1, 13, 0).toISOString(),
      duration_minutes: 50,
      reason: 'Sleep hygiene follow-up',
      meeting_link: 'https://meet.google.com/abc-defg-hij'
    }
  ];

  let sessions = $state<CalendarSession[]>(mockSessionsSeed);
  let mode = $state<ViewMode>('month');
  let activeStatus = $state<SessionStatus | 'all'>('all');
  let activeType = $state<SessionType | 'all'>('all');

  let focusedDate = $state(new Date());

  const monthLabelFormat = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric'
  });

  const dayTitleFormat = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  const timeLabelFormat = new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });

  let focusedDateISO = $derived(focusedDate.toISOString().slice(0, 10));
  let monthLabel = $derived(monthLabelFormat.format(focusedDate));

  let filteredSessions = $derived(
    sessions
      .filter((s) => activeStatus === 'all' || s.status === activeStatus)
      .filter((s) => activeType === 'all' || s.appointment_type === activeType)
      .sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at))
  );

  let sessionsByDay = $derived.by(() => {
    const map = new Map<string, CalendarSession[]>();
    for (const session of filteredSessions) {
      const day = session.scheduled_at.slice(0, 10);
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

    return Array.from({ length: total }, (_, i) => {
      const dayDate = new Date(focusedDate.getFullYear(), focusedDate.getMonth(), i - leading + 1);
      const iso = dayDate.toISOString().slice(0, 10);
      const daySessions = sessionsByDay.get(iso) ?? [];
      return {
        iso,
        dayNumber: dayDate.getDate(),
        inMonth: dayDate.getMonth() === focusedDate.getMonth(),
        isToday: iso === new Date().toISOString().slice(0, 10),
        total: daySessions.length,
        hasConfirmed: daySessions.some((s) => s.status === 'confirmed'),
        hasPending: daySessions.some((s) => s.status === 'pending')
      };
    });
  });

  let weekSessions = $derived.by(() => {
    const start = new Date(focusedDate);
    start.setDate(focusedDate.getDate() - focusedDate.getDay());

    return Array.from({ length: 7 }, (_, index) => {
      const day = new Date(start);
      day.setDate(start.getDate() + index);
      const iso = day.toISOString().slice(0, 10);
      return {
        iso,
        label: dayTitleFormat.format(day),
        sessions: sessionsByDay.get(iso) ?? []
      };
    });
  });

  let daySessions = $derived(sessionsByDay.get(focusedDateISO) ?? []);

  let nextSession = $derived(
    filteredSessions.find((s) => +new Date(s.scheduled_at) > Date.now()) ?? null
  );

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

  function formatTime(iso: string) {
    return timeLabelFormat.format(new Date(iso));
  }

  function statusClass(status: SessionStatus) {
    if (status === 'confirmed') return 'bg-emerald-100 text-emerald-700';
    if (status === 'pending') return 'bg-amber-100 text-amber-700';
    if (status === 'completed') return 'bg-blue-100 text-blue-700';
    return 'bg-rose-100 text-rose-700';
  }

  function approveSession(id: string) {
    sessions = sessions.map((s) => (s.id === id ? { ...s, status: 'confirmed' } : s));
  }

  function markCompleted(id: string) {
    sessions = sessions.map((s) => (s.id === id ? { ...s, status: 'completed' } : s));
  }

  function cancelSession(id: string) {
    sessions = sessions.map((s) => (s.id === id ? { ...s, status: 'cancelled' } : s));
  }

  function generateMeetingLink(id: string) {
    sessions = sessions.map((s) =>
      s.id === id
        ? {
            ...s,
            meeting_link: s.meeting_link ?? `https://meet.google.com/${id.replace(/-/g, '').slice(0, 10)}`
          }
        : s
    );
  }
</script>

<svelte:head>
  <title>Therapist Calendar — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Therapist Calendar</p>
    <h1 class="mt-2 text-2xl font-semibold text-blue-950 sm:text-3xl">Session Planning Workspace</h1>
    <p class="mt-1 text-sm text-slate-600">
      Month/Week/Day calendar with backend-aligned actions: confirm, cancel, complete, and generate meeting links.
    </p>
  </header>

  <div class="grid gap-6 lg:grid-cols-[1.55fr_1fr]">
    <article class="space-y-4 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <Button variant="outline" class="border-blue-200 text-blue-700" onclick={() => shiftDate(-1)}>
            ←
          </Button>
          <h2 class="text-lg font-semibold text-blue-900">{monthLabel}</h2>
          <Button variant="outline" class="border-blue-200 text-blue-700" onclick={() => shiftDate(1)}>
            →
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
        </select>

        <select bind:value={activeType} class="rounded-lg border border-blue-200 px-3 py-2 text-sm">
          <option value="all">All session types</option>
          <option value="video">Video</option>
          <option value="in_person">In person</option>
          <option value="phone">Phone</option>
        </select>
      </div>

      {#if mode === 'month'}
        <div class="grid grid-cols-7 gap-2 text-center text-xs font-semibold uppercase tracking-wide text-blue-500">
          <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
        </div>

        <div class="grid grid-cols-7 gap-2">
          {#each monthGrid as day (day.iso)}
            <button
              type="button"
              class={`relative min-h-20 rounded-xl border p-2 text-left text-sm transition ${
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
            <article class="rounded-xl border border-blue-100 p-3">
              <h3 class="font-medium text-blue-900">{day.label}</h3>
              {#if day.sessions.length === 0}
                <p class="mt-2 text-sm text-slate-500">No sessions</p>
              {:else}
                <ul class="mt-2 space-y-2 text-sm">
                  {#each day.sessions as session (session.id)}
                    <li class="rounded-lg bg-blue-50 px-2 py-1.5">
                      <p class="font-medium text-blue-900">{formatTime(session.scheduled_at)} — {session.patient_name}</p>
                      <p class="text-slate-600">{session.appointment_type}</p>
                    </li>
                  {/each}
                </ul>
              {/if}
            </article>
          {/each}
        </div>
      {:else}
        <article class="space-y-3 rounded-xl border border-blue-100 p-4">
          <h3 class="font-medium text-blue-900">{new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).format(focusedDate)}</h3>
          {#if daySessions.length === 0}
            <p class="text-sm text-slate-500">No sessions scheduled for this day.</p>
          {:else}
            <ul class="space-y-2">
              {#each daySessions as session (session.id)}
                <li class="rounded-lg bg-blue-50 px-3 py-2 text-sm text-slate-700">
                  <p class="font-medium text-blue-900">{formatTime(session.scheduled_at)} — {session.patient_name}</p>
                  <p>{session.duration_minutes} min • {session.appointment_type}</p>
                </li>
              {/each}
            </ul>
          {/if}
        </article>
      {/if}
    </article>

    <aside class="space-y-4">
      <article class="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm">
        <h3 class="text-sm font-semibold text-blue-900">Next Session</h3>
        {#if nextSession}
          <p class="mt-2 text-sm font-medium text-blue-900">{nextSession.patient_name}</p>
          <p class="text-sm text-slate-700">{dayTitleFormat.format(new Date(nextSession.scheduled_at))} at {formatTime(nextSession.scheduled_at)}</p>
          <p class="mt-1 text-xs text-slate-500">{nextSession.reason}</p>
        {:else}
          <p class="mt-2 text-sm text-slate-500">No upcoming sessions for selected filters.</p>
        {/if}
      </article>

      <article class="space-y-3 rounded-2xl border border-blue-100 bg-white p-4 shadow-sm">
        <h3 class="text-sm font-semibold text-blue-900">Session Queue</h3>
        {#if filteredSessions.length === 0}
          <p class="text-sm text-slate-500">No sessions available.</p>
        {:else}
          {#each filteredSessions.slice(0, 5) as session (session.id)}
            <div class="rounded-xl border border-slate-200 p-3">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="font-medium text-blue-900">{session.patient_name}</p>
                  <p class="text-xs text-slate-600">{dayTitleFormat.format(new Date(session.scheduled_at))} • {formatTime(session.scheduled_at)}</p>
                </div>
                <span class={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${statusClass(session.status)}`}>
                  {session.status}
                </span>
              </div>

              <p class="mt-2 text-xs text-slate-600">{session.reason}</p>

              <div class="mt-3 flex flex-wrap gap-2">
                {#if session.status === 'pending'}
                  <Button class="bg-blue-600 text-white hover:bg-blue-700" onclick={() => approveSession(session.id)}>
                    Confirm
                  </Button>
                {/if}

                {#if session.status === 'confirmed'}
                  <Button variant="outline" class="border-emerald-300 text-emerald-700 hover:bg-emerald-50" onclick={() => markCompleted(session.id)}>
                    Complete
                  </Button>
                  <Button variant="outline" class="border-rose-300 text-rose-700 hover:bg-rose-50" onclick={() => cancelSession(session.id)}>
                    Cancel
                  </Button>
                  <Button variant="outline" class="border-blue-300 text-blue-700 hover:bg-blue-50" onclick={() => generateMeetingLink(session.id)}>
                    {session.meeting_link ? 'Refresh Meet Link' : 'Generate Meet Link'}
                  </Button>
                {/if}

                {#if session.meeting_link}
                  <a href={session.meeting_link} target="_blank" rel="noreferrer" class="inline-flex">
                    <Button variant="outline" class="border-blue-200 text-blue-700 hover:bg-blue-50">Open Link</Button>
                  </a>
                {/if}
              </div>
            </div>
          {/each}
        {/if}
      </article>
    </aside>
  </div>
</section>
