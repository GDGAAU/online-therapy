import type { TherapistAvailabilitySlot } from '$lib/types';
import type { TimeSlot } from '$lib/components/booking/TherapistCalendar.svelte';

export function formatDateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function formatFee(fee: string | null | undefined) {
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

export function formatExperience(years: number) {
  return `${years} ${years === 1 ? 'year' : 'years'} experience`;
}

export function formatSessionType(type: string) {
  return type.replace('_', ' ');
}

export function formatTime(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value));
}

export function getDurationMinutes(slot: TherapistAvailabilitySlot) {
  const start = new Date(slot.start_at).getTime();
  const end = new Date(slot.end_at).getTime();
  const duration = Math.round((end - start) / 60_000);
  return Number.isFinite(duration) && duration > 0 ? duration : 50;
}

export function adaptAvailability(
  response: Record<string, TherapistAvailabilitySlot[]>
): Record<string, TimeSlot[]> {
  return Object.fromEntries(
    Object.entries(response).map(([date, slots]) => [
      date,
      slots.map((slot, index) => ({
        id: `${slot.start_at}-${index}`,
        time: formatTime(slot.start_at),
        status: slot.is_available ? 'available' : 'booked',
        startAt: slot.start_at,
        duration_minutes: getDurationMinutes(slot)
      }))
    ])
  );
}
