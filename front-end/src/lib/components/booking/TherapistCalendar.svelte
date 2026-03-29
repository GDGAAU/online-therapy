<script lang="ts">
  export type SlotStatus = 'available' | 'booked';

  export interface TimeSlot {
    id: string;
    time: string;
    status: SlotStatus;
    startAt: string;
    duration_minutes: number;
  }

  interface DayCell {
    isoDate: string;
    dayNumber: number;
    inCurrentMonth: boolean;
    hasAvailable: boolean;
    hasBooked: boolean;
    isToday: boolean;
  }

  interface Props {
    availability: Record<string, TimeSlot[]>;
    selectedDate?: string;
    selectedSlot?: string;
  }

  let {
    availability,
    selectedDate = $bindable(''),
    selectedSlot = $bindable('')
  }: Props = $props();

  let visibleMonth = $state(new Date());

  const monthFormatter = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric'
  });

  const dayNumberFormatter = new Intl.DateTimeFormat('en-US', {
    day: '2-digit'
  });

  const fullDateFormatter = new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });

  let monthLabel = $derived(monthFormatter.format(visibleMonth));

  let dayCells = $derived(
    (() => {
      const firstDayOfMonth = new Date(
        visibleMonth.getFullYear(),
        visibleMonth.getMonth(),
        1
      );
      const lastDayOfMonth = new Date(
        visibleMonth.getFullYear(),
        visibleMonth.getMonth() + 1,
        0
      );

      const leadingDays = firstDayOfMonth.getDay();
      const daysInMonth = lastDayOfMonth.getDate();
      const totalCells = Math.ceil((leadingDays + daysInMonth) / 7) * 7;

      const rows: DayCell[] = [];
      const todayIso = new Date().toISOString().slice(0, 10);

      for (let idx = 0; idx < totalCells; idx += 1) {
        const date = new Date(
          visibleMonth.getFullYear(),
          visibleMonth.getMonth(),
          idx - leadingDays + 1
        );
        const isoDate = date.toISOString().slice(0, 10);
        const slots = availability[isoDate] ?? [];

        rows.push({
          isoDate,
          dayNumber: Number(dayNumberFormatter.format(date)),
          inCurrentMonth: date.getMonth() === visibleMonth.getMonth(),
          hasAvailable: slots.some((slot) => slot.status === 'available'),
          hasBooked: slots.some((slot) => slot.status === 'booked'),
          isToday: isoDate === todayIso
        });
      }

      return rows;
    })()
  );

  let selectedDateLabel = $derived(
    selectedDate
      ? fullDateFormatter.format(new Date(`${selectedDate}T00:00:00`))
      : 'Choose a day to begin'
  );

  let slotsForSelectedDate = $derived(
    selectedDate ? (availability[selectedDate] ?? []) : []
  );

  $effect(() => {
    if (selectedDate) return;

    const firstBookableDay = dayCells.find(
      (day) => day.inCurrentMonth && day.hasAvailable
    );

    if (firstBookableDay) {
      selectedDate = firstBookableDay.isoDate;
    }
  });

  $effect(() => {
    if (!selectedDate || !selectedSlot) return;

    const slot = (availability[selectedDate] ?? []).find((s) => s.id === selectedSlot);
    if (!slot || slot.status !== 'available') {
      selectedSlot = '';
    }
  });

  function previousMonth() {
    visibleMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() - 1, 1);
  }

  function nextMonth() {
    visibleMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 1);
  }

  function chooseDay(day: DayCell) {
    if (!day.inCurrentMonth) return;
    selectedDate = day.isoDate;
    selectedSlot = '';
  }

  function chooseSlot(slot: TimeSlot) {
    if (slot.status !== 'available') return;
    selectedSlot = slot.id;
  }
</script>

<section class="space-y-6 rounded-2xl border border-blue-100 bg-white p-5 shadow-sm" aria-label="Therapy booking calendar">
  <div class="flex items-center justify-between gap-3">
    <button
      type="button"
      class="rounded-xl border border-blue-100 p-2 text-blue-700 transition hover:bg-blue-50"
      aria-label="Previous month"
      onclick={previousMonth}
    >
      ←
    </button>

    <h3 class="text-base font-semibold text-blue-900 sm:text-lg">{monthLabel}</h3>

    <button
      type="button"
      class="rounded-xl border border-blue-100 p-2 text-blue-700 transition hover:bg-blue-50"
      aria-label="Next month"
      onclick={nextMonth}
    >
      →
    </button>
  </div>

  <div class="grid grid-cols-7 gap-2 text-center text-xs font-semibold uppercase tracking-wide text-blue-500">
    <span>Sun</span>
    <span>Mon</span>
    <span>Tue</span>
    <span>Wed</span>
    <span>Thu</span>
    <span>Fri</span>
    <span>Sat</span>
  </div>

  <div class="grid grid-cols-7 gap-2">
  {#snippet dayButton(day: DayCell)}
      <button
        type="button"
        class={`relative min-h-11 rounded-xl border text-sm transition focus:outline-none focus:ring-2 focus:ring-blue-400 ${
          day.inCurrentMonth
            ? 'border-blue-100 bg-white text-blue-900 hover:bg-blue-50'
            : 'border-transparent bg-blue-50/40 text-blue-300'
        } ${
          selectedDate === day.isoDate
            ? 'border-blue-500 bg-blue-600 text-white hover:bg-blue-600'
            : ''
        }`}
        disabled={!day.inCurrentMonth}
        aria-pressed={selectedDate === day.isoDate}
        aria-label={`Select ${day.isoDate}`}
        onclick={() => chooseDay(day)}
      >
        <span>{day.dayNumber}</span>
        {#if day.inCurrentMonth && day.isToday}
          <span class="absolute left-1/2 top-1 -translate-x-1/2 text-[10px] font-semibold">Today</span>
        {/if}
        {#if day.inCurrentMonth && day.hasAvailable}
          <span class={`absolute bottom-1 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full ${
            selectedDate === day.isoDate ? 'bg-white' : 'bg-emerald-500'
          }`}></span>
        {:else if day.inCurrentMonth && day.hasBooked}
          <span class={`absolute bottom-1 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full ${
            selectedDate === day.isoDate ? 'bg-white/80' : 'bg-rose-400'
          }`}></span>
        {/if}
      </button>
    {/snippet}

    {#each dayCells as day (day.isoDate)}
      {@render dayButton(day)}
    {/each}
  </div>

  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-blue-900">{selectedDateLabel}</p>
      <p class="text-xs text-blue-500">Green = available • Red = booked</p>
    </div>

    {#if !selectedDate}
      <p class="rounded-xl border border-dashed border-blue-200 p-3 text-sm text-blue-500">
        Pick a date to view available therapy sessions.
      </p>
    {:else if slotsForSelectedDate.length === 0}
      <p class="rounded-xl border border-dashed border-blue-200 p-3 text-sm text-blue-500">
        No sessions configured for this date.
      </p>
    {:else}
      <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
  {#snippet slotButton(slot: TimeSlot)}
          <button
            type="button"
            class={`rounded-xl border px-3 py-2 text-sm font-medium transition ${
              slot.status === 'booked'
                ? 'cursor-not-allowed border-rose-200 bg-rose-50 text-rose-500'
                : selectedSlot === slot.id
                  ? 'border-blue-600 bg-blue-600 text-white'
                  : 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
            }`}
            disabled={slot.status === 'booked'}
            aria-pressed={selectedSlot === slot.id}
            onclick={() => chooseSlot(slot)}
          >
            {slot.time}
          </button>
        {/snippet}

        {#each slotsForSelectedDate as slot (slot.id)}
          {@render slotButton(slot)}
        {/each}
      </div>
    {/if}
  </div>
</section>
