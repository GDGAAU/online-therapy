<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils";

	export let className = "";
	export { className as class };
	export let ref: HTMLParagraphElement | null = null;

	const _unused: HTMLAttributes<HTMLParagraphElement> | undefined = undefined;
</script>

<p
	bind:this={ref}
	data-slot="card-description"
	class={cn("text-muted-foreground text-sm", className)}
	{...$$restProps}
>
	<slot />
</p>
