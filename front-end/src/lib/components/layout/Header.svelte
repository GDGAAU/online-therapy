<script lang="ts">
  import logoImg from "$lib/assets/logo.png";
  import { authStore, logout } from "$lib/stores/auth";
  import { Button } from "$lib/components/ui/button";
</script>

<header class="sticky top-0 z-40 w-full border-b border-blue-100 bg-white/95 backdrop-blur">
  <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
    <div class="flex items-center gap-3">
      <button
        type="button"
        class="inline-flex items-center justify-center rounded-full border border-blue-100 bg-white p-2 text-blue-600 shadow-sm transition hover:bg-blue-50 md:hidden"
        aria-label="Open navigation"
      >
        <svg
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <a href="/" class="flex items-center gap-2">
        <img src={logoImg} alt="online therapy" class="h-8 w-auto" />
        <span class="text-lg font-semibold tracking-wide text-blue-900 md:text-xl">
          online-therapy
        </span>
      </a>
    </div>

    <nav class="hidden items-center gap-6 text-sm font-medium text-blue-900 md:flex">
      <a href="/" class="hover:text-blue-600">Home</a>
      <a href="/blog" class="hover:text-blue-600">Blog</a>
      <a href="/search" class="hover:text-blue-600">Find a therapist</a>
    </nav>

    <div class="flex items-center gap-3">
      {#if $authStore.user}
        <a href={`/profile/${$authStore.user.id}`} aria-label="View profile">
          <Button
            variant="outline"
            size="icon"
            class="rounded-full border-blue-200 text-blue-600 hover:bg-blue-50"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 20c2-4 6-6 8-6s6 2 8 6" />
            </svg>
          </Button>
        </a>
        <Button
          variant="outline"
          class="border-blue-200 text-blue-600 hover:bg-blue-50"
          on:click={logout}
        >
          Log out
        </Button>
      {:else}
        <a href="/login" aria-label="Log in">
          <Button
            variant="outline"
            size="icon"
            class="rounded-full border-blue-200 text-blue-600 hover:bg-blue-50"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M10 17l5-5-5-5" />
              <path d="M15 12H3" />
              <path d="M21 19a2 2 0 0 1-2 2h-5" />
              <path d="M21 5a2 2 0 0 0-2-2h-5" />
            </svg>
          </Button>
        </a>
      {/if}
    </div>
  </div>
</header>
