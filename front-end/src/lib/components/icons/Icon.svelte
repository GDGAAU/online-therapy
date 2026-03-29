<script lang="ts">
  export type IconName =
    | 'search'
    | 'xmark'
    | 'eye'
    | 'eye-slash'
    | 'spinner'
    | 'arrow-left'
    | 'bell'
    | 'clock'
    | 'plus'
    | 'user-circle'
    | 'check-circle';

  const { name, size = 20, class: className = '' } = $props<{
    name: IconName;
    size?: number;
    class?: string;
  }>();
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class={className}
>
  {#if name === 'search'}
    <circle cx="11" cy="11" r="7" />
    <line x1="16.65" y1="16.65" x2="21" y2="21" />
  {:else if name === 'xmark'}
    <line x1="6" y1="6" x2="18" y2="18" />
    <line x1="6" y1="18" x2="18" y2="6" />
  {:else if name === 'eye'}
    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" />
    <circle cx="12" cy="12" r="3" />
  {:else if name === 'eye-slash'}
    <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.77 21.77 0 0 1 5.06-5.94" />
    <path d="M9.88 9.88A3 3 0 0 0 12 15a3 3 0 0 0 2.12-.88" />
    <path d="M3 3l18 18" />
  {:else if name === 'spinner'}
    <circle cx="12" cy="12" r="9" stroke-opacity="0.25" />
    <path d="M21 12a9 9 0 0 0-9-9" />
  {:else if name === 'arrow-left'}
    <line x1="19" y1="12" x2="5" y2="12" />
    <polyline points="12 19 5 12 12 5" />
  {:else if name === 'bell'}
    <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  {:else if name === 'clock'}
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 3" />
  {:else if name === 'plus'}
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  {:else if name === 'user-circle'}
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="10" r="3" />
    <path d="M6 18c1.5-2.5 4-4 6-4s4.5 1.5 6 4" />
  {:else if name === 'check-circle'}
    <circle cx="12" cy="12" r="10" />
    <path d="M9 12l2 2 4-4" />
  {/if}
</svg>
