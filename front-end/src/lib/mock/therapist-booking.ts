import type { AppointmentType, Therapist } from "$lib/types";

export interface MockTherapistDetail extends Therapist {
  bio: string;
  license_number: string;
}

export interface MockAvailabilitySlot {
  id: string;
  time: string;
  status: "available" | "booked";
  startAt: string;
  duration_minutes: number;
}

const THERAPIST_ID = "34d5742c-03c9-46b9-8e1a-77c5f4baf422";

export const mockTherapistsById: Record<string, MockTherapistDetail> = {
  [THERAPIST_ID]: {
    id: THERAPIST_ID,
    name: "Dr. Lena Whitmore",
    specialties: [
      {
        id: "46df45ca-4f11-419e-a55c-f76b19fba5dc",
        name: "Psychotherapy",
        slug: "psychotherapy",
      },
      {
        id: "c1d73d96-2e7f-4f8f-947c-7e67760ddda5",
        name: "Anxiety Counseling",
        slug: "anxiety-counseling",
      },
    ],
    years_of_experience: 11,
    is_available: true,
    consultation_fee: "120.00",
    avatar_url: null,
    bio: "I help adults navigate burnout, anxiety, and relationship stress with practical, compassionate therapy sessions. My approach blends cognitive and mindfulness techniques tailored to your pace.",
    license_number: "THP-LN-22819",
  },
};

const SLOT_TEMPLATE = [
  { hour: 9, minute: 0, label: "09:00 AM" },
  { hour: 10, minute: 30, label: "10:30 AM" },
  { hour: 12, minute: 0, label: "12:00 PM" },
  { hour: 14, minute: 30, label: "02:30 PM" },
  { hour: 16, minute: 0, label: "04:00 PM" },
];

export function buildMockAvailability(
  startDate = new Date(),
  numberOfDays = 28,
  durationMinutes = 50,
  appointmentType: AppointmentType = "video",
): Record<string, MockAvailabilitySlot[]> {
  const availability: Record<string, MockAvailabilitySlot[]> = {};

  for (let dayOffset = 0; dayOffset < numberOfDays; dayOffset += 1) {
    const date = new Date(
      startDate.getFullYear(),
      startDate.getMonth(),
      startDate.getDate() + dayOffset,
    );

    if (date.getDay() === 0) continue;

    const isoDate = date.toISOString().slice(0, 10);

    availability[isoDate] = SLOT_TEMPLATE.map((template, index) => {
      const startAt = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate(),
        template.hour,
        template.minute,
        0,
      );

      const deterministicSeed = dayOffset + index;
      const status = deterministicSeed % 4 === 0 ? "booked" : "available";

      return {
        id: `${isoDate}-${template.hour}-${template.minute}-${appointmentType}`,
        time: template.label,
        status,
        startAt: startAt.toISOString(),
        duration_minutes: durationMinutes,
      };
    });
  }

  return availability;
}

export const defaultMockTherapistId = THERAPIST_ID;
