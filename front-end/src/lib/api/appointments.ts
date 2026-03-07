/**
 * lib/api/appointments.ts
 * ========================
 * Appointment and therapist API calls.
 */

import { apiClient } from "./client";
import type {
  Appointment,
  PaginatedResponse,
  Therapist,
  CreateAppointmentPayload,
} from "$lib/types";

export const therapyApi = {
  // ─── Therapists ─────────────────────────────────────────

  /** List all available therapists. Filter by specialty slug. */
  listTherapists: (specialty?: string) =>
    apiClient.get<PaginatedResponse<Therapist>>(
      `/therapy/therapists/${specialty ? `?specialty=${specialty}` : ""}`,
    ),

  /** Get a single therapist's full profile. */
  getTherapist: (id: string) =>
    apiClient.get<Therapist>(`/therapy/therapists/${id}/`),

  // ─── Appointments ────────────────────────────────────────

  /** List the current user's appointments. Filter by status. */
  listAppointments: (appointmentStatus?: string) =>
    apiClient.get<PaginatedResponse<Appointment>>(
      `/therapy/appointments/${appointmentStatus ? `?status=${appointmentStatus}` : ""}`,
    ),

  /** Get a single appointment. */
  getAppointment: (id: string) =>
    apiClient.get<Appointment>(`/therapy/appointments/${id}/`),

  /** Book a new appointment. */
  createAppointment: (data: CreateAppointmentPayload) =>
    apiClient.post<Appointment>("/therapy/appointments/", data),

  /** Cancel an appointment. */
  cancelAppointment: (id: string, reason?: string) =>
    apiClient.post<{ message: string }>(`/therapy/appointments/${id}/cancel/`, {
      reason,
    }),
};
