<script lang="ts">
  import { Search, X } from 'lucide-svelte';
  import { Input } from '$lib/components/ui/input';
  
  export let value: string = '';
  export let placeholder: string = 'Search...';
  export let onSearch: (query: string) => void = () => {};
  
  
  function handleClear() {
    value = '';
    onSearch('');
  }
  
  function handleSubmit(event: Event) {
    event.preventDefault();
    onSearch(value);
  }
</script>

<form on:submit={handleSubmit} class="relative w-full">
  <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-black" size={18} />
  
 <Input
  type="search"
  {placeholder}
  bind:value
  className="pl-10 pr-10 h-12 rounded-full bg-[#ECF1FF] placeholder-[#809CFF] transition-all focus:ring-0 focus:ring-offset-0 focus:border-2 focus:border-[#809CFF]"
/>
  {#if value}
    <button
      type="button"
      on:click={handleClear}
      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
      aria-label="Clear search"
    >
      <X size={16} />
    </button>
  {/if}
</form>