<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { logout } from '$lib/stores/auth';
  import { Button } from '$lib/components/ui/button';

  export let data: { username: string } | undefined;

  const goBack = () => {
    if (browser && window.history.length > 1) {
      window.history.back();
      return;
    }

    goto('/');
  };
</script>

<svelte:head>
  <title>Profile — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-3xl p-6">
  <div class="mb-4 flex items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <button
        type="button"
        on:click={goBack}
        class="inline-flex items-center justify-center rounded-full border border-blue-100 bg-white p-2 text-blue-600 shadow-sm transition hover:bg-blue-50"
        aria-label="Go back"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <h1 class="text-2xl font-semibold text-gray-900">Profile</h1>
    </div>
    <Button variant="outline" className="border-blue-200 text-blue-600" on:click={logout}>
      Log out
    </Button>
  </div>
  <p class="text-gray-500 mt-2">Profile for <strong>{data?.username ?? 'user'}</strong> will render here.</p>
</section>
