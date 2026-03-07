<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils";

	export let className = "";
	export { className as class };
	export let ref: HTMLDivElement | null = null;

	const _unused: HTMLAttributes<HTMLDivElement> | undefined = undefined;
</script>

<div bind:this={ref} data-slot="card-content" class={cn("px-6", className)} {...$$restProps}>
	<slot />
</div>
