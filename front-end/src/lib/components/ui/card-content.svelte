<script lang="ts">
  import { cn } from '$lib/utils';
  interface Props {
    className?: string;
    children?: import('svelte').Snippet;
  }

  let { className = '', children }: Props = $props();
</script>

<div class={cn('p-6', className)}>
  {@render children?.()}
</div>
