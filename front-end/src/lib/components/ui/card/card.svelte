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
	data-slot="card"
	class={cn(
		"bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
		className
	)}
	{...rest}
>
	{@render children?.()}
</div>
