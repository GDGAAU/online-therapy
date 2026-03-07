<script lang="ts">
  import type { HTMLLabelAttributes } from 'svelte/elements';
  import { cn } from '$lib/utils';

  export let className: string = '';
  export let forValue: HTMLLabelAttributes['for'] = undefined;
</script>

<label
  for={forValue}
  class={cn('text-sm font-medium text-gray-700', className)}
  {...$$restProps}
>
  <slot />
</label>
