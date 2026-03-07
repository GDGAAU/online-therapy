/**
 * lib/api/index.ts
 * =================
 * Single entry point for all API modules.
 *
 * Usage:
 *   import { authApi, therapyApi } from '$lib/api';
 */

export { apiClient, tokenStorage, ApiError } from "./client";
export type { ApiErrorShape } from "./client";
export { authApi } from "./auth";
export { therapyApi } from "./appointments";
