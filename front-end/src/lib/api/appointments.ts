/**
 * lib/api/appointments.ts
 * ========================
 * Appointment and therapist API calls.
 */

import { apiClient } from "./client";
import type {
  Appointment,
  PaginatedResponse,
  Specialty,
  Therapist,
  TherapistAvailabilitySlot,
  TherapistListParams,
  TherapistProfileUpdatePayload,
  CreateAppointmentPayload,
  RescheduleAppointmentPayload,
} from "$lib/types";

function buildTherapistQuery(params?: string | TherapistListParams) {
  if (!params) return "";

  const query = new URLSearchParams();

  if (typeof params === "string") {
    query.set("specialty", params);
  } else {
    if (params.search) query.set("search", params.search);
    if (params.specialty) query.set("specialty", params.specialty);
    if (params.page) query.set("page", String(params.page));
    if (params.page_size) query.set("page_size", String(params.page_size));
  }

  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export const therapyApi = {
  // ─── Therapists ─────────────────────────────────────────

  /** List therapists. Filter by text search, specialty slug, or pagination params. */
  listTherapists: (params?: string | TherapistListParams) =>
    apiClient.get<PaginatedResponse<Therapist>>(
      `/therapy/therapists/${buildTherapistQuery(params)}`,
    ),

  /** List therapy specialties used by therapist filters. */
  listSpecialties: () =>
    apiClient.get<PaginatedResponse<Specialty>>("/therapy/specialties/"),

  /** Get a single therapist's full profile. */
  getTherapist: (id: string) =>
    apiClient.get<Therapist>(`/therapy/therapists/${id}/`),

  /** Get the authenticated therapist's own profile. */
  getCurrentTherapistProfile: () =>
    apiClient.get<Therapist>("/therapy/therapists/me/"),

  /** Update the authenticated therapist's own profile. */
  updateCurrentTherapistProfile: (data: TherapistProfileUpdatePayload) =>
    apiClient.patch<Therapist>("/therapy/therapists/me/", data),

  /** Get therapist availability between two YYYY-MM-DD dates. */
  getTherapistAvailability: (id: string, dateFrom: string, dateTo: string) =>
    apiClient.get<Record<string, TherapistAvailabilitySlot[]>>(
      `/therapy/therapists/${id}/availability/?from=${dateFrom}&to=${dateTo}`,
    ),

  // ─── Appointments ────────────────────────────────────────

  /** List the current user's appointments. Filter by status. */
  listAppointments: (appointmentStatus?: string, role?: "patient" | "therapist") => {
    const query = new URLSearchParams();
    if (appointmentStatus) query.set("status", appointmentStatus);
    if (role) query.set("role", role);
    const queryString = query.toString();

    return apiClient.get<PaginatedResponse<Appointment>>(
      `/therapy/appointments/${queryString ? `?${queryString}` : ""}`,
    );
  },

  /** Get a single appointment. */
  getAppointment: (id: string) =>
    apiClient.get<Appointment>(`/therapy/appointments/${id}/`),

  /** Book a new appointment. */
  createAppointment: (data: CreateAppointmentPayload) =>
    apiClient.post<Appointment>("/therapy/appointments/", data),

  /** Reschedule an existing appointment. */
  rescheduleAppointment: (id: string, data: RescheduleAppointmentPayload) =>
    apiClient.post<{ message: string; appointment: Appointment }>(
      `/therapy/appointments/${id}/reschedule/`,
      data,
    ),

  /** Confirm a pending appointment as the therapist. */
  confirmAppointment: (id: string) =>
    apiClient.post<{ message: string }>(`/therapy/appointments/${id}/confirm/`),

  /** Mark a confirmed appointment complete as the therapist. */
  completeAppointment: (id: string) =>
    apiClient.post<{ message: string }>(`/therapy/appointments/${id}/complete/`),

  /** Generate or return the meeting link for a confirmed appointment. */
  generateMeetingLink: (id: string) =>
    apiClient.post<{ meeting_link: string }>(
      `/therapy/appointments/${id}/generate-meeting-link/`,
    ),

  /** Cancel an appointment. */
  cancelAppointment: (id: string, reason?: string) =>
    apiClient.post<{ message: string }>(`/therapy/appointments/${id}/cancel/`, {
      reason,
    }),
};
