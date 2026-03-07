/**
 * lib/api/client.ts
 * ==================
 * Base Axios API client.
 *
 * Features:
 * - Automatic JWT token injection from localStorage
 * - 401 → auto token refresh, then retry original request
 * - Typed responses via generics
 * - Consistent error shape thrown as ApiError
 *
 * Usage:
 *   import { apiClient } from '$lib/api/client';
 *   const data = await apiClient.get<User>('/auth/me/');
 */

import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";
import { env } from "$env/dynamic/public";
import { browser } from "$app/environment";
import { goto } from "$app/navigation";

// ─── Types ──────────────────────────────────────────────────

export interface ApiErrorShape {
  code: string;
  message: string;
  detail: unknown;
}

export class ApiError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly detail: unknown;

  constructor(message: string, status: number, code: string, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.detail = detail ?? null;
  }
}

// ─── Token Storage ──────────────────────────────────────────

const TOKEN_KEY = "ot_access_token";
const REFRESH_COOKIE = "ot_refresh_token";

const refreshCookieOptions = () => {
  const secureFlag =
    browser && window.location.protocol === "https:" ? "; Secure" : "";
  return `Path=/; Max-Age=${60 * 60 * 24 * 7}; SameSite=Lax${secureFlag}`;
};

const getCookie = (name: string): string | null => {
  if (!browser) return null;
  const match = document.cookie.match(
    new RegExp(
      `(?:^|; )${name.replace(/([.$?*|{}()\[\]\\/\+^])/g, "\\$1")}=([^;]*)`,
    ),
  );
  return match ? decodeURIComponent(match[1]) : null;
};

export const tokenStorage = {
  getAccess: (): string | null =>
    browser ? localStorage.getItem(TOKEN_KEY) : null,
  getRefresh: (): string | null => getCookie(REFRESH_COOKIE),
  set: (access: string, refresh: string) => {
    if (!browser) return;
    localStorage.setItem(TOKEN_KEY, access);
    document.cookie = `${REFRESH_COOKIE}=${encodeURIComponent(refresh)}; ${refreshCookieOptions()}`;
  },
  clear: () => {
    if (!browser) return;
    localStorage.removeItem(TOKEN_KEY);
    document.cookie = `${REFRESH_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
  },
};

// ─── Axios Instance ─────────────────────────────────────────

const API_BASE_URL = env.PUBLIC_API_URL ?? "/api/v1";

const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

// ─── Request Interceptor: Attach Access Token ────────────────

axiosInstance.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Track in-flight refresh to avoid double-refresh ────────

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function notifyRefreshDone(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

// ─── Response Interceptor: Handle 401 / errors ───────────────

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 401 → try refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = tokenStorage.getRefresh();

      if (!refreshToken) {
        tokenStorage.clear();
        if (browser) goto("/login");
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise((resolve) => {
          subscribeRefresh((newToken: string) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post(`${API_BASE_URL}/auth/jwt/refresh/`, {
          refresh: refreshToken,
        });

        tokenStorage.set(data.access, data.refresh ?? refreshToken);
        notifyRefreshDone(data.access);
        isRefreshing = false;

        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return axiosInstance(originalRequest);
      } catch {
        isRefreshing = false;
        tokenStorage.clear();
        if (browser) goto("/login");
        return Promise.reject(error);
      }
    }

    // Shape error into ApiError
    const errorData = error.response?.data?.error;
    throw new ApiError(
      errorData?.message ?? error.message ?? "An unexpected error occurred.",
      error.response?.status ?? 0,
      errorData?.code ?? "UNKNOWN_ERROR",
      errorData?.detail ?? null,
    );
  },
);

// ─── Typed Convenience Methods ───────────────────────────────

export const apiClient = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.get<T>(url, config).then((r) => r.data),

  post: <T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> => axiosInstance.post<T>(url, data, config).then((r) => r.data),

  patch: <T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> =>
    axiosInstance.patch<T>(url, data, config).then((r) => r.data),

  put: <T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> => axiosInstance.put<T>(url, data, config).then((r) => r.data),

  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    axiosInstance.delete<T>(url, config).then((r) => r.data),
};
