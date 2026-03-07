/**
 * lib/stores/auth.ts
 * ===================
 * Svelte writable store for authentication state.
 *
 * Provides:
 * - Current user profile (null when logged out)
 * - Loading state
 * - login / logout / refresh helpers
 *
 * Usage:
 *   import { authStore, login, logout } from '$lib/stores/auth';
 *   $authStore.user → UserProfile | null
 */

import { writable, derived, get } from "svelte/store";
import { goto } from "$app/navigation";
import { browser } from "$app/environment";
import { authApi, tokenStorage } from "$lib/api";
import type { UserProfile } from "$lib/types";

// ─── State Shape ─────────────────────────────────────────────

interface AuthState {
  user: UserProfile | null;
  isLoading: boolean;
  isInitialized: boolean;
}

// ─── Store ───────────────────────────────────────────────────

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    isLoading: false,
    isInitialized: false,
  });

  return {
    subscribe,

    /** Initialize auth state on app boot by fetching current user. */
    async initialize() {
      if (!browser) return;

      const token = tokenStorage.getAccess();
      if (!token) {
        update((s) => ({ ...s, isInitialized: true }));
        return;
      }

      update((s) => ({ ...s, isLoading: true }));
      try {
        const user = await authApi.getMe();
        update((s) => ({ ...s, user, isLoading: false, isInitialized: true }));
      } catch {
        tokenStorage.clear();
        update((s) => ({
          ...s,
          user: null,
          isLoading: false,
          isInitialized: true,
        }));
      }
    },

    /** Set user after login. */
    setUser(user: UserProfile) {
      update((s) => ({ ...s, user }));
    },

    /** Clear user on logout. */
    clear() {
      set({ user: null, isLoading: false, isInitialized: true });
    },
  };
}

export const authStore = createAuthStore();

/** Derived: is the user currently logged in? */
export const isAuthenticated = derived(
  authStore,
  ($auth) => $auth.user !== null,
);

// ─── Auth Actions ─────────────────────────────────────────────

export async function login(email: string, password: string): Promise<void> {
  await authApi.login({ email, password });
  const user = await authApi.getMe();
  authStore.setUser(user);
  await goto("/dashboard");
}

export async function logout(): Promise<void> {
  await authApi.logout();
  authStore.clear();
  await goto("/login");
}
