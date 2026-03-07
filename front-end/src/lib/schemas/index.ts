/**
 * lib/schemas/index.ts
 * =====================
 * Zod schemas for all forms, used with sveltekit-superforms.
 *
 * Keep these in sync with backend serializer validation rules.
 */

import { z } from "zod";

// ─── Auth Schemas ─────────────────────────────────────────────

export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});

export const registerSchema = z
  .object({
    full_name: z
      .string()
      .min(2, "Full name is required.")
      .max(150, "Full name is too long."),
    date_of_birth: z.string().min(1, "Date of birth is required."),
    phone_number: z.string().min(7, "Phone number is required."),
    email: z.string().email("Please enter a valid email address."),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter.")
      .regex(/[0-9]/, "Password must contain at least one number."),
    re_password: z.string(),
  })
  .refine((data) => data.password === data.re_password, {
    message: "Passwords do not match.",
    path: ["re_password"],
  });

export const forgotPasswordSchema = z.object({
  email: z.string().email("Please enter a valid email address."),
});

export const resetPasswordSchema = z
  .object({
    token: z.string().min(1),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter.")
      .regex(/[0-9]/, "Password must contain at least one number."),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match.",
    path: ["confirm_password"],
  });

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required."),
    new_password: z
      .string()
      .min(8, "New password must be at least 8 characters."),
    confirm_new_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_new_password, {
    message: "Passwords do not match.",
    path: ["confirm_new_password"],
  });

// ─── Profile Schema ───────────────────────────────────────────

export const updateProfileSchema = z.object({
  first_name: z.string().max(150).optional(),
  last_name: z.string().max(150).optional(),
  bio: z.string().optional(),
  phone_number: z.string().max(20).optional(),
  date_of_birth: z.string().optional(),
});

// ─── Appointment Schema ───────────────────────────────────────

export const bookAppointmentSchema = z.object({
  therapist_id: z.string().uuid("Invalid therapist."),
  scheduled_at: z.string().min(1, "Please select a date and time."),
  appointment_type: z.enum(["in_person", "video", "phone"]),
  reason: z.string().optional(),
});

export const cancelAppointmentSchema = z.object({
  reason: z.string().optional(),
});

// ─── Inferred Types ───────────────────────────────────────────

export type LoginSchema = z.infer<typeof loginSchema>;
export type RegisterSchema = z.infer<typeof registerSchema>;
export type ForgotPasswordSchema = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordSchema = z.infer<typeof resetPasswordSchema>;
export type BookAppointmentSchema = z.infer<typeof bookAppointmentSchema>;
