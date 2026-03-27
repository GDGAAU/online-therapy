<script lang="ts">
	import { cn } from "$lib/utils";
	import { buttonVariants, type ButtonSize, type ButtonVariant } from "./variants";

	
	interface Props {
		variant?: ButtonVariant;
		size?: ButtonSize;
		href?: string | undefined;
		type?: "button" | "submit" | "reset";
		disabled?: boolean | undefined;
		class?: string;
		ref?: HTMLButtonElement | HTMLAnchorElement | null;
		children?: import('svelte').Snippet;
		[key: string]: any
	}

	let {
		variant = "default",
		size = "default",
		href = undefined,
		type = "button",
		disabled = undefined,
		class: className = "",
		ref = $bindable(null),
		children,
		...rest
	}: Props = $props();
</script>

{#if href}
	<a
		bind:this={ref}
		data-slot="button"
		class={cn(buttonVariants({ variant, size }), className)}
		href={disabled ? undefined : href}
		aria-disabled={disabled}
		role={disabled ? "link" : undefined}
		tabindex={disabled ? -1 : undefined}
		{...rest}
	>
		{@render children?.()}
	</a>
{:else}
	<button
		bind:this={ref}
		data-slot="button"
		class={cn(buttonVariants({ variant, size }), className)}
		{type}
		{disabled}
		{...rest}
	>
		{@render children?.()}
	</button>
{/if}
