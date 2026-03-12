<script lang="ts">
  import type { HTMLTextareaAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  interface Props {
    className?: string;
    value?: HTMLTextareaAttributes['value'];
    [key: string]: any
  }

  let { className = '', value = $bindable(undefined), ...rest }: Props = $props();
</script>

<textarea
  bind:value
  class={cn(
    'flex min-h-[80px] w-full rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm transition-colors placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
    className
  )}
  {...rest}
></textarea>
