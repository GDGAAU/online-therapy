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
  import { sidebarOpen, closeSidebar } from '$lib/stores/ui';
  import { env } from '$env/dynamic/public';
  import Header from '$lib/components/layout/Header.svelte';
  import Sidebar from './(auth_required)/dashboard/components/Sidebar.svelte';
  import '../app.css';
  import { page } from '$app/stores';

  interface Props {
    data: any; 
    params: Record<string, string>;
    children?: import('svelte').Snippet;
  }

  let { data, params, children }: Props = $props();

  let stateSnapshot = $derived({ data, params });
  let isDashboardRoute = $derived($page.url.pathname.startsWith('/dashboard'));

  $effect(() => {
    if (!browser) return;
    document.body.classList.toggle('overflow-hidden', isDashboardRoute && $sidebarOpen);

    return () => {
      document.body.classList.remove('overflow-hidden');
    };
  });

  onMount(async () => {
    await authStore.initialize();

    if (env.PUBLIC_SENTRY_DSN) {
      const { init } = await import('@sentry/sveltekit');
      init({ dsn: env.PUBLIC_SENTRY_DSN, tracesSampleRate: 0.1 });
    }
  });
</script>


<Toaster position="top-right" richColors closeButton />

<Header />

{#if isDashboardRoute}
  <Sidebar bind:clicked={$sidebarOpen} />

  {#if $sidebarOpen}
    <button
      type="button"
      class="fixed inset-0 z-40 bg-black/30"
      aria-label="Close sidebar"
      onclick={closeSidebar}
    ></button>
  {/if}
{/if}

<main>
  {@render children?.()}
</main>
