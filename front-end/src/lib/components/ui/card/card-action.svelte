<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils";

	
	interface Props {
		class?: string;
		ref?: HTMLDivElement | null;
		children?: import('svelte').Snippet;
		[key: string]: any
	}

	let { class: className = "", ref = $bindable(null), children, ...rest }: Props = $props();

	const _unused: HTMLAttributes<HTMLDivElement> | undefined = undefined;
</script>

<div
	bind:this={ref}
	data-slot="card-action"
	class={cn("col-start-2 row-span-2 row-start-1 self-start justify-self-end", className)}
	{...rest}
>
	{@render children?.()}
</div>
