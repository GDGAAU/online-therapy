<script lang="ts">
  import Button from '$lib/components/ui/button/button.svelte';
  import { authStore, logout } from '$lib/stores/auth';

  let { clicked = $bindable() } = $props();

  function closeSidebar() {
    clicked = false;
  }

  async function handleLogout() {
    closeSidebar();
    await logout();
  }
</script>

<aside
  class="fixed bottom-0 left-0 top-0 z-50 w-[82%] transform border border-black bg-white transition-transform duration-300 md:w-[25%]"
  class:translate-x-0={clicked}
  class:-translate-x-full={!clicked}
>
  <div class="flex items-center gap-4 border border-b-2 border-gray-200 py-2.25">
    <div class="rounded-full p-1.5">
      <i class="fa-regular fa-circle-user text-4xl"></i>
    </div>
    <div>
      <h1 class="font-bold">{$authStore.user?.first_name ?? 'Therapist'}</h1>
      <p>Therapist</p>
    </div>
  </div>

  <nav class="my-5 flex flex-col items-start justify-start">
    <a href="/therapist-dashboard" class="w-full">
      <Button
        class="flex w-full cursor-pointer flex-row items-center justify-start rounded-none bg-white py-2 text-black hover:bg-gray-100 active:bg-gray-200 focus:bg-linear-to-r focus:from-[#3870FF] focus:to-[#38B7FF] focus:text-white"
        onclick={closeSidebar}
      >
        <i class="fa-solid fa-house text-xl text-slate-600"></i>
        <p>Dashboard</p>
      </Button>
    </a>

    <a href="/calendar" class="w-full">
      <Button
        class="flex w-full cursor-pointer flex-row items-center justify-start rounded-none bg-white py-2 text-black hover:bg-gray-100 active:bg-gray-200 focus:bg-linear-to-r focus:from-[#3870FF] focus:to-[#38B7FF] focus:text-white"
        onclick={closeSidebar}
      >
        <i class="fa-solid fa-calendar-days text-xl text-slate-600"></i>
        <p>Calendar</p>
      </Button>
    </a>

    <a href="/notifications" class="w-full">
      <Button
        class="flex w-full cursor-pointer flex-row items-center justify-start rounded-none bg-white py-2 text-black hover:bg-gray-100 active:bg-gray-200 focus:bg-linear-to-r focus:from-[#3870FF] focus:to-[#38B7FF] focus:text-white"
        onclick={closeSidebar}
      >
        <i class="fa-solid fa-bell text-xl text-slate-600"></i>
        <p>Notifications</p>
      </Button>
    </a>

    <a href="/blog" class="w-full">
      <Button
        class="flex w-full cursor-pointer flex-row items-center justify-start rounded-none bg-white py-2 text-black hover:bg-gray-100 active:bg-gray-200 focus:bg-linear-to-r focus:from-[#3870FF] focus:to-[#38B7FF] focus:text-white"
        onclick={closeSidebar}
      >
        <i class="fa-solid fa-hand-holding-heart text-xl text-slate-600"></i>
        <p>Wellness Blogs</p>
      </Button>
    </a>
  </nav>

  <div class="mt-2">
    <Button
      class="flex w-full cursor-pointer flex-row items-center justify-start rounded-none bg-white py-2 text-black hover:bg-gray-100 active:bg-gray-200"
      onclick={handleLogout}
    >
      <i class="fa-solid fa-arrow-right-from-bracket"></i>
      <p>Log out</p>
    </Button>
  </div>
</aside>
