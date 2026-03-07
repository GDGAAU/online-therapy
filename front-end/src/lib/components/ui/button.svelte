<script lang="ts">
  import type { HTMLButtonAttributes } from 'svelte/elements';
  import { createEventDispatcher } from 'svelte';
  import { cn } from '$lib/utils';

  const dispatch = createEventDispatcher<{ click: MouseEvent }>();

  export let variant: 'default' | 'outline' | 'ghost' | 'secondary' | 'destructive' = 'default';
  export let size: 'sm' | 'md' | 'lg' | 'icon' = 'md';
  export let className: string = '';

  const variants: Record<typeof variant, string> = {
    default: 'bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50',
    outline: 'border border-gray-200 text-gray-700 hover:bg-gray-50',
    ghost: 'text-gray-700 hover:bg-gray-100',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    destructive: 'bg-red-500 text-white hover:bg-red-600 disabled:opacity-50'
  };

  const sizes: Record<typeof size, string> = {
    sm: 'h-9 px-3 rounded-lg text-sm',
    md: 'h-10 px-4 rounded-xl',
    lg: 'h-11 px-6 rounded-xl text-base',
    icon: 'h-10 w-10 rounded-full'
  };

  export let type: HTMLButtonAttributes['type'] = 'button';
  export let disabled: HTMLButtonAttributes['disabled'] = false;
</script>

<button
  {type}
  {disabled}
  class={cn(
    'inline-flex items-center justify-center gap-2 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2',
    variants[variant],
    sizes[size],
    className
  )}
  on:click={(event) => dispatch('click', event)}
  {...$$restProps}
>
  <slot />
</button>
