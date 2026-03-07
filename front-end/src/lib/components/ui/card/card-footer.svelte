<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils";

	export let className = "";
	export { className as class };
	export let ref: HTMLDivElement | null = null;

	const _unused: HTMLAttributes<HTMLDivElement> | undefined = undefined;
</script>

<div
	bind:this={ref}
	data-slot="card-footer"
	class={cn("flex items-center px-6 [.border-t]:pt-6", className)}
	{...$$restProps}
>
	<slot />
</div>
