
<script>
    import Nav from "./components/Nav.svelte";
    import WelcomeBlock from "./components/WelcomeBlock.svelte";
    import MiniStatCard from "./components/MiniStatCard.svelte";
    import Status from "./components/Status.svelte";
    import Sidebar from "./components/Sidebar.svelte";
//toggle side bar
    let isOpen = $state(false);
    function toggleSidebar() {
        isOpen = !isOpen;
    }
    $effect(() => {
	document.body.classList.toggle("overflow-hidden", isOpen);

	return () => {
		document.body.classList.remove("overflow-hidden");
	};
});



</script>
<Sidebar bind:clicked={isOpen} />

{#if isOpen}
	<div
		class="fixed inset-0 bg-black/30 z-40"
		onclick={() => isOpen = false}
	></div>
{/if}

<section class="relative z-0">
	<Nav color="#000" bgColor="#fff" OnToggle={toggleSidebar} />
	<WelcomeBlock />
	<MiniStatCard />
	<Status />
</section>