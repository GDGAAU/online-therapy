/**
 * lib/types/index.ts
 * ===================
 * Shared TypeScript types for the entire frontend.
 * Kept in sync with backend serializer shapes.
 */

// ─── Auth ────────────────────────────────────────────────────

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  phone_number: string;
  date_of_birth: string;
  password: string;
  re_password: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface MessageResponse {
  message: string;
}

// ─── User / Profile ──────────────────────────────────────────

export interface UserProfile {
  id: string;
  email: string;
  user_type: "patient" | "therapist" | "admin";
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  bio: string;
  phone_number: string;
  date_of_birth: string | null;
}

export type UpdateProfilePayload = Partial<
  Pick<
    UserProfile,
    "first_name" | "last_name" | "bio" | "phone_number" | "date_of_birth"
  >
>;

// ─── Therapy ─────────────────────────────────────────────────

export interface Specialty {
  id: string;
  name: string;
  slug: string;
}

export interface Therapist {
  id: string;
  name: string;
  specialties: Specialty[];
  years_of_experience: number;
  is_available: boolean;
  consultation_fee: string | null;
  avatar_url: string | null;
  bio?: string;
}

export type AppointmentStatus =
  | "pending"
  | "confirmed"
  | "completed"
  | "cancelled"
  | "no_show";

export type AppointmentType = "in_person" | "video" | "phone";

export interface Appointment {
  id: string;
  therapist: string;
  therapist_name: string;
  therapist_specialty: string[];
  status: AppointmentStatus;
  appointment_type: AppointmentType;
  scheduled_at: string;
  duration_minutes: number;
  reason: string;
  created_at: string;
}

export interface CreateAppointmentPayload {
  therapist_id: string;
  scheduled_at: string;
  appointment_type: AppointmentType;
  reason?: string;
}

// ─── Shared ──────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
}

/** API error shape returned by the backend. */
export interface ApiErrorDetail {
  error: {
    code: string;
    message: string;
    detail: unknown;
  };
}
