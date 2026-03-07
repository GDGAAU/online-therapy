<script lang="ts">
  import type { HTMLTextareaAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  export let className: string = '';
  export let value: HTMLTextareaAttributes['value'] = undefined;
</script>

<textarea
  bind:value
  class={cn(
    'flex min-h-[80px] w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    className
  )}
  {...$$restProps}
/>
