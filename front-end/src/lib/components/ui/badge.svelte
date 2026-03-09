<script lang="ts">
  import { cn } from '$lib/utils';

  interface Props {
    variant?: 'default' | 'secondary' | 'success' | 'warning' | 'destructive';
    className?: string;
    children?: import('svelte').Snippet;
  }

  let { variant = 'default', className = '', children }: Props = $props();

  const variants: Record<typeof variant, string> = {
    default: 'bg-blue-100 text-blue-700',
    secondary: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    destructive: 'bg-red-100 text-red-700'
  };
</script>

<span
  class={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold', variants[variant], className)}
>
  {@render children?.()}
</span>
