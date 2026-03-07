// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { UserProfile } from "$lib/types";

declare global {
  namespace App {
    interface Error {
      code?: string;
    }
    interface Locals {
      user: UserProfile | null;
    }
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

export {};
