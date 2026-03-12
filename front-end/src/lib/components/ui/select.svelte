<script lang="ts">
  import type { HTMLSelectAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  interface Props {
    className?: string;
    value?: HTMLSelectAttributes['value'];
    children?: import('svelte').Snippet;
    [key: string]: any
  }

  let { className = '', value = $bindable(undefined), children, ...rest }: Props = $props();
</script>

<select
  bind:value
  class={cn(
    'flex h-10 w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    className
  )}
  {...rest}
>
  {@render children?.()}
</select>
