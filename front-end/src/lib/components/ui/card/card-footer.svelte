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
	data-slot="card-footer"
	class={cn("flex items-center px-6 [.border-t]:pt-6", className)}
	{...rest}
>
	{@render children?.()}
</div>
