/**
 * lib/api/auth.ts
 * ================
 * All authentication-related API calls.
 *
 * Follows the createMindplexSdk pattern from the spec but adapted
 * to the Django backend and structured as standalone module functions.
 */

import { apiClient, tokenStorage } from "./client";
import type {
  LoginPayload,
  RegisterPayload,
  TokenPair,
  MessageResponse,
  UserProfile,
  UpdateProfilePayload,
} from "$lib/types";

export const authApi = {
  /**
   * Register a new account.
   * Backend sends a verification email — user must activate before login.
   */
  register: (data: RegisterPayload) =>
    apiClient.post<MessageResponse>("/auth/users/", data),

  /**
   * Verify email with the token from the activation email link.
   */
  activateAccount: (uid: string, token: string) =>
    apiClient.post<MessageResponse>("/auth/users/activation/", { uid, token }),

  /**
   * Request a new activation email (e.g. if original expired).
   */
  resendActivation: (email: string) =>
    apiClient.post<MessageResponse>("/auth/users/resend_activation/", {
      email,
    }),

  /**
   * Login and receive JWT token pair.
   * Automatically stores the access token in localStorage and refresh token in cookies.
   */
  login: async (data: LoginPayload): Promise<TokenPair> => {
    const tokens = await apiClient.post<TokenPair>("/auth/jwt/create/", data);
    tokenStorage.set(tokens.access, tokens.refresh);
    return tokens;
  },

  /**
   * Logout — clear tokens locally.
   * (Backend token blacklisting happens automatically on refresh expiry.)
   */
  logout: async () => {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) {
        await apiClient.post<MessageResponse>("/auth/logout/", { refresh });
      }
    } finally {
      tokenStorage.clear();
    }
  },

  /**
   * Request a password reset email.
   */
  forgotPassword: (email: string) =>
    apiClient.post<MessageResponse>("/auth/users/reset_password/", { email }),

  /**
   * Reset password using the token from the reset email.
   */
  resetPassword: (data: {
    uid: string;
    token: string;
    new_password: string;
    re_new_password: string;
  }) =>
    apiClient.post<MessageResponse>(
      "/auth/users/reset_password_confirm/",
      data,
    ),

  /**
   * Change password for an authenticated user.
   */
  changePassword: (data: {
    current_password: string;
    new_password: string;
    confirm_new_password: string;
  }) =>
    apiClient.post<MessageResponse>("/auth/users/set_password/", {
      current_password: data.current_password,
      new_password: data.new_password,
      re_new_password: data.confirm_new_password,
    }),

  /**
   * Google OAuth login — pass the ID token from Google Sign-In.
   * Automatically stores tokens.
   */
  googleLogin: async (idToken: string): Promise<TokenPair> => {
    const tokens = await apiClient.post<TokenPair>("/auth/google/", {
      id_token: idToken,
    });
    tokenStorage.set(tokens.access, tokens.refresh);
    return tokens;
  },

  /**
   * Get the current authenticated user's profile.
   */
  getMe: () => apiClient.get<UserProfile>("/auth/users/me/"),

  /**
   * Update the current user's profile.
   */
  updateMe: (data: UpdateProfilePayload) =>
    apiClient.patch<UserProfile>("/auth/users/me/", data),
};
