<script lang="ts">
  import { cn } from '$lib/utils';
  export let className: string = '';
</script>

<div class={cn('rounded-2xl border border-gray-100 bg-white shadow-sm', className)}>
  <slot />
</div>
