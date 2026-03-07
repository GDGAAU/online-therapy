<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  export let className: string = '';
  export let type: HTMLInputAttributes['type'] = 'text';
  export let value: HTMLInputAttributes['value'] = undefined;

  function handleInput(event: Event) {
    value = (event.currentTarget as HTMLInputElement).value;
  }
</script>

<input
  {type}
  {value}
  on:input={handleInput}
  class={cn(
    'flex h-10 w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    className
  )}
  {...$$restProps}
/>
