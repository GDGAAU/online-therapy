<script lang="ts">
  import Icon from '$lib/components/icons/Icon.svelte';
  import { Input } from '$lib/components/ui/input';
  
  let { value = $bindable(''), placeholder = 'Search...', onSearch = () => {} } = $props<{
    value?: string;
    placeholder?: string;
    onSearch?: (query: string) => void;
  }>();
  
  
  function handleClear() {
    value = '';
    onSearch('');
  }
  
  function handleSubmit(event: Event) {
    event.preventDefault();
    onSearch(value);
  }
</script>

<form onsubmit={handleSubmit} class="relative w-full">
  <Icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 text-black" size={18} />
  
 <Input
  type="search"
  {placeholder}
  bind:value
  className="pl-10 pr-10 h-12 rounded-full bg-[#ECF1FF] placeholder-[#809CFF] transition-all focus:ring-0 focus:ring-offset-0 focus:border-2 focus:border-[#809CFF]"
/>
  {#if value}
    <button
      type="button"
      onclick={handleClear}
      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Clear search"
    >
      <Icon name="xmark" size={16} />
    </button>
  {/if}
</form>
