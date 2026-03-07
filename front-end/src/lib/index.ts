/**
 * lib/index.ts
 * =============
 * Barrel exports for the `$lib` alias.
 *
 * Import anything from $lib:
 *   import { authApi, authStore, loginSchema } from '$lib';
 *
 * Or import directly from sub-modules for tree-shaking:
 *   import { authApi } from '$lib/api';
 */

// API
export * from "./api";

// Types
export type * from "./types";

// Schemas
export * from "./schemas";

// Stores
export * from "./stores/auth";

// UI utils
export * from "./utils";
