<script lang="ts">
	import { cn } from "$lib/utils";
	import { buttonVariants, type ButtonSize, type ButtonVariant } from "./variants";

	export let variant: ButtonVariant = "default";
	export let size: ButtonSize = "default";
	export let href: string | undefined = undefined;
	export let type: "button" | "submit" | "reset" = "button";
	export let disabled: boolean | undefined = undefined;
	export let className = "";
	export { className as class };
	export let ref: HTMLButtonElement | HTMLAnchorElement | null = null;
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
		{...$$restProps}
	>
		<slot />
	</a>
{:else}
	<button
		bind:this={ref}
		data-slot="button"
		class={cn(buttonVariants({ variant, size }), className)}
		{type}
		{disabled}
		{...$$restProps}
	>
		<slot />
	</button>
{/if}
