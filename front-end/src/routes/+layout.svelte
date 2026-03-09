<script lang="ts">
  import { onMount } from 'svelte';
  import { Toaster } from 'svelte-sonner';
  import { browser } from '$app/environment';
  import { authStore } from '$lib/stores/auth';
  import { env } from '$env/dynamic/public';
  import Header from '$lib/components/layout/Header.svelte';
  import '../app.css';

  interface Props {
    data: any; 
    params: Record<string, string>;
    children?: import('svelte').Snippet;
  }

  let { data, params, children }: Props = $props();

  let stateSnapshot = $derived({ data, params });

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

<main>
  {@render children?.()}
</main>
