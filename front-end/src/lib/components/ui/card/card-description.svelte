<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "$lib/utils";

	
	interface Props {
		class?: string;
		ref?: HTMLParagraphElement | null;
		children?: import('svelte').Snippet;
		[key: string]: any
	}

	let { class: className = "", ref = $bindable(null), children, ...rest }: Props = $props();

	const _unused: HTMLAttributes<HTMLParagraphElement> | undefined = undefined;
</script>

<p
	bind:this={ref}
	data-slot="card-description"
	class={cn("text-muted-foreground text-sm", className)}
	{...rest}
>
	{@render children?.()}
</p>
