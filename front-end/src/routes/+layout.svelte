<script lang="ts">
  /**
   * Root layout
   * Runs on every page. Initializes:
   * - Auth state (fetch /me if token exists)
   * - Sonner toast container
   * - Sentry (if DSN is set)
   */
  import { onMount } from 'svelte';
  import { Toaster } from 'svelte-sonner';
  import { browser } from '$app/environment';
  import { authStore } from '$lib/stores/auth';
  import { env } from '$env/dynamic/public';
  import Header from '$lib/components/layout/Header.svelte';
  import '../app.css';

  export let data: unknown;
  export let params: Record<string, string>;

  const _unused = [data, params];

  onMount(async () => {
    // Initialize auth state on app load
    await authStore.initialize();

    // Initialize Sentry in production
    if (env.PUBLIC_SENTRY_DSN) {
      const { init } = await import('@sentry/sveltekit');
      init({ dsn: env.PUBLIC_SENTRY_DSN, tracesSampleRate: 0.1 });
    }
  });
</script>

<!-- Sonner toast container — renders toasts from anywhere in the app -->
{#if browser}
  <Toaster position="top-right" richColors closeButton />
{/if}

<Header />

<main>
  <slot />
</main>
