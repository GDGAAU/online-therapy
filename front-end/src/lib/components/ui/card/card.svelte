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
	data-slot="card"
	class={cn(
		"bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
		className
	)}
	{...$$restProps}
>
	<slot />
</div>
