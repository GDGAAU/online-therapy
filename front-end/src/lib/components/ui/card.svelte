<script lang="ts">
  import { cn } from '$lib/utils';
  interface Props {
    className?: string;
    children?: import('svelte').Snippet;
  }

  let { className = '', children }: Props = $props();
</script>

<div class={cn('rounded-2xl border border-gray-100 bg-white shadow-sm', className)}>
  {@render children?.()}
</div>
