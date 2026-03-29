<script lang="ts">
  import logoImg from "$lib/assets/logo.png";
  import { authStore, logout } from "$lib/stores/auth";
  import { Button } from "$lib/components/ui/button";
  import { page } from "$app/stores";
  import { toggleSidebar } from "$lib/stores/ui";

  let isDashboardPage = $derived($page.url.pathname.startsWith('/dashboard'));
  let mobileMenuOpen = $state(false);
</script>

<header class="sticky top-0 z-40 w-full border-b border-blue-100 bg-white/95 backdrop-blur">
  <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3">
    <div class="flex items-center gap-2">
      {#if isDashboardPage}
        <Button
          type="button"
          variant="outline"
          size="icon"
          class="rounded-full border-blue-200 text-blue-600 hover:bg-blue-50"
          aria-label="Open sidebar"
          onclick={toggleSidebar}
        >
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
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
        </Button>
      {/if}
      <a href="/" class="flex items-center gap-2">
        <img src={logoImg} alt="online therapy" class="h-8 w-auto" />
        <span class="hidden text-lg font-semibold tracking-wide text-blue-900 sm:inline md:text-xl">
          online-therapy
        </span>
      </a>
    </div>

    <nav class="hidden items-center gap-6 text-sm font-medium text-blue-900 md:flex">
      <a href="/" class="hover:text-blue-600">Home</a>
      <a href="/blog" class="hover:text-blue-600">Blog</a>
      <a href="/search" class="hover:text-blue-600">Find a therapist</a>
      {#if $authStore.user}
        <a href="/dashboard" class="hover:text-blue-600">Dashboard</a>
      {/if}
    </nav>

    <div class="flex items-center gap-2 sm:gap-3">
      {#if isDashboardPage}
        <a href="/notifications" aria-label="View alerts">
          <Button
            variant="outline"
            size="icon"
            class="rounded-full border-blue-200 text-blue-600 hover:bg-blue-50"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </Button>
        </a>
      {/if}
      {#if !isDashboardPage}
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full border border-blue-100 bg-white p-2 text-blue-600 shadow-sm transition hover:bg-blue-50 md:hidden"
          aria-label="Toggle menu"
          onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
        >
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
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
      {/if}
      {#if $authStore.user}
        <a
          href={`/profile/${$authStore.user.id}`}
          aria-label="View profile"
          class={isDashboardPage ? "" : "hidden md:block"}
        >
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
          class={isDashboardPage
            ? "border-blue-200 text-blue-600 hover:bg-blue-50"
            : "hidden border-blue-200 text-blue-600 hover:bg-blue-50 md:inline-flex"}
          onclick={logout}
        >
          Log out
        </Button>
      {:else}
        <a href="/login" class={isDashboardPage ? "" : "hidden md:inline-flex"}>
          <Button variant="outline" class="border-blue-200 text-blue-600 hover:bg-blue-50">
            <span class="hidden sm:inline">Log in</span>
            <span class="sm:hidden">Login</span>
          </Button>
        </a>
        <a href="/signup" class={isDashboardPage ? "" : "hidden md:inline-flex"}>
          <Button class="bg-blue-600 text-white hover:bg-blue-700">
            <span class="hidden sm:inline">Sign up</span>
            <span class="sm:hidden">Join</span>
          </Button>
        </a>
      {/if}
    </div>
  </div>

  {#if mobileMenuOpen && !isDashboardPage}
    <div class="border-t border-blue-100 bg-white/95 px-4 py-4 md:hidden">
      <nav class="flex flex-col gap-3 text-sm font-medium text-blue-900">
        <a href="/" class="hover:text-blue-600" onclick={() => (mobileMenuOpen = false)}>Home</a>
        <a href="/blog" class="hover:text-blue-600" onclick={() => (mobileMenuOpen = false)}>Blog</a>
        <a href="/search" class="hover:text-blue-600" onclick={() => (mobileMenuOpen = false)}>
          Find a therapist
        </a>
        <a href="/appointment" class="hover:text-blue-600" onclick={() => (mobileMenuOpen = false)}>
          Appointments
        </a>
        {#if $authStore.user}
          <a href="/dashboard" class="hover:text-blue-600" onclick={() => (mobileMenuOpen = false)}>
            Dashboard
          </a>
        {/if}
      </nav>

      <div class="mt-4 flex flex-col gap-3">
        {#if $authStore.user}
          <a href={`/profile/${$authStore.user.id}`} onclick={() => (mobileMenuOpen = false)}>
            <Button variant="outline" class="w-full border-blue-200 text-blue-600 hover:bg-blue-50">
              Profile
            </Button>
          </a>
          <Button
            variant="outline"
            class="w-full border-blue-200 text-blue-600 hover:bg-blue-50"
            onclick={() => {
              logout();
              mobileMenuOpen = false;
            }}
          >
            Log out
          </Button>
        {:else}
          <a href="/login" onclick={() => (mobileMenuOpen = false)}>
            <Button variant="outline" class="w-full border-blue-200 text-blue-600 hover:bg-blue-50">
              Log in
            </Button>
          </a>
          <a href="/signup" onclick={() => (mobileMenuOpen = false)}>
            <Button class="w-full bg-blue-600 text-white hover:bg-blue-700">Sign up</Button>
          </a>
        {/if}
      </div>
    </div>
  {/if}
</header>
