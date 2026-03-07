<script lang="ts">
  import type { HTMLSelectAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  export let className: string = '';
  export let value: HTMLSelectAttributes['value'] = undefined;
</script>

<select
  bind:value
  class={cn(
    'flex h-10 w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    className
  )}
  {...$$restProps}
>
  <slot />
</select>
