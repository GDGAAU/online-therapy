<script>
    import Button from "$lib/components/ui/button/button.svelte";
    import { authStore } from "@";
    let { clicked = $bindable() } = $props();
    let image = $state(false);
    function onclick() {
        clicked = false;
    }
</script>

<aside
    class="md:w-[25%] w-[80%] bg-[#FFFFFF] border border-black
     bottom-0 fixed top-0 left-0 transform transition-transform duration-300 z-50"
    class:translate-x-0={clicked}
    class:-translate-x-full={!clicked}
>
    <div
        class="flex items-center gap-4 border border-b-2 border-gray-200 py-[9px]"
    >
        <div class="rounded-full p-1.5">
            {#if image}
                <img src="" alt="" aria-hidden="true" class="rounded-full" />
            {:else}
                <i class="fa-regular fa-circle-user text-4xl"></i>
            {/if}
        </div>
        <div>
            <h1 class="font-bold">{authStore.user}</h1>
            <p>Patient</p>
        </div>
    </div>

    <nav class="flex flex-col items-start justify-start my-5">
        <a href="/dashboard" class="w-full">
            <Button
                class="flex flex-row justify-start items-center bg-white
                            text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer
                            focus:bg-linear-to-r from-[#3870FF] to-[#38B7FF] focus:text-white "
                {onclick}
            >
                <i class="fa-solid fa-house text-xl text-slate-600"> </i>
                <p>Dashboard</p>
            </Button>
        </a>
        <a href="/" class="w-full">
            <Button
                class="flex flex-row justify-start items-center bg-white
            text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer 
            focus:bg-linear-to-r from-[#3870FF] to-[#38B7FF] focus:text-white"
                {onclick}
            >
                <i class="fa-solid fa-calendar-check text-xl text-slate-600"></i>
                <p>Appointments</p>
            </Button>
        </a>

        <a href="/" class="w-full">
            <Button
                class="flex flex-row justify-start items-center bg-white
            text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer
            focus:bg-linear-to-r from-[#3870FF] to-[#38B7FF] focus:text-white "
                {onclick}
            >
                <i class="fa-solid fa-users text-xl text-slate-600"></i>
                <p>Queue Status</p>
            </Button>
        </a>

        <a href="/" class="w-full">
            <Button
                class="flex flex-row justify-start items-center bg-white
            text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer 
            focus:bg-linear-to-r from-[#3870FF] to-[#38B7FF] focus:text-white"
                {onclick}
            >
                <i class="fa-solid fa-pills text-xl text-slate-600"></i>
                <p>Medications</p>
            </Button>
        </a>

        <a href="/" class="w-full">
            <Button
                class="flex flex-row justify-start items-center bg-white
            text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer
            focus:bg-linear-to-r from-[#3870FF] to-[#38B7FF] focus:text-white "
                {onclick}
            >
                <i class="fa-solid fa-hand-holding-heart text-xl text-slate-600"
                ></i>
                <p>Wellness Blogs</p>
            </Button>
            </a>
    </nav>

    <div
        class="bg-[#ECF1FF] border border-[#809CFF] rounded-xl mt-4 mx-4 p-4 space-y-3 text-left"
    >
        <div class="flex items-center gap-3">
            <i class="fa-solid fa-comment text-lg"></i>
            <p class="font-semibold">AI Assistant</p>
        </div>

    <p class="text-sm text-[#656565] wrap-break-word">
            Ask me about appointments, medications.
        </p>

        <Button class="bg-[#3870FF] flex items-center justify-center w-full gap-2">
            <i class="fa-solid fa-comment text-base"></i>
            <p>Start Chat</p>
        </Button>
    </div>

    <div class="mt-2">
        <Button
            class="flex flex-row justify-start items-center bg-white text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer"
            {onclick}
        >
            <i class="fa-regular fa-moon"></i>
            <p>Dark Mode</p>
        </Button>
        <Button
            class="flex flex-row justify-start items-center bg-white text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer"
            {onclick}
        >
            <i class="fa-solid fa-gear"></i>
            <p>Setting</p>
        </Button>
        <Button
            class="flex flex-row justify-start items-center bg-white text-black w-full rounded-none py-2 hover:bg-gray-100 active:bg-gray-200 cursor-pointer"
            {onclick}
        >
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
            <p>Log out</p>
        </Button>
    </div>
</aside>
