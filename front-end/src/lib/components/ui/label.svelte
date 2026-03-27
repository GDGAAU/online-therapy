<script lang="ts">
  import type { HTMLLabelAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  interface Props {
    className?: string;
    forValue?: HTMLLabelAttributes['for'];
    children?: import('svelte').Snippet;
    [key: string]: any
  }

  let { className = '', forValue = undefined, children, ...rest }: Props = $props();
</script>

<label
  for={forValue}
  class={cn('text-sm font-medium text-gray-700', className)}
  {...rest}
>
  {@render children?.()}
</label>
