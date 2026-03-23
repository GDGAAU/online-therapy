<script lang="ts">
  import type { HTMLButtonAttributes } from 'svelte/elements';
  import { createEventDispatcher } from 'svelte';
  import { cn } from '$lib/utils';

  const dispatch = createEventDispatcher<{ click: MouseEvent }>();

  //  Added for type-script compatability
  type Variant = 'default' | 'outline' | 'ghost' | 'secondary' | 'destructive';
  type Size = 'sm' | 'md' | 'lg' | 'icon';

  const variants: Record<Variant, string> = {
    default: 'bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50',
    outline: 'border border-gray-200 text-gray-700 hover:bg-gray-50',
    ghost: 'text-gray-700 hover:bg-gray-100',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    destructive: 'bg-red-500 text-white hover:bg-red-600 disabled:opacity-50'
  };

  const sizes: Record<Size, string> = {
    sm: 'h-9 px-3 rounded-lg text-sm',
    md: 'h-10 px-4 rounded-xl',
    lg: 'h-11 px-6 rounded-xl text-base',
    icon: 'h-10 w-10 rounded-full'
  };

  interface Props {
    variant?: 'default' | 'outline' | 'ghost' | 'secondary' | 'destructive';
    size?: 'sm' | 'md' | 'lg' | 'icon';
    className?: string;
    type?: HTMLButtonAttributes['type'];
    disabled?: HTMLButtonAttributes['disabled'];
    children?: import('svelte').Snippet;
    [key: string]: any
  }

  let {
    variant = 'default',
    size = 'md',
    className = '',
    type = 'button',
    disabled = false,
    children,
    ...rest
  }: Props = $props();
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
  onclick={(event) => dispatch('click', event)}
  {...rest}
>
  {@render children?.()}
</button>
