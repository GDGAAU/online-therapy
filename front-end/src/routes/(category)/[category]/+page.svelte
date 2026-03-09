<script lang="ts">
  interface Props {
    data: { category: string } | undefined;
  }

  let { data }: Props = $props();
</script>

<svelte:head>
  <title>Category — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-3xl p-6">
  <h1 class="text-2xl font-semibold text-gray-900">Category</h1>
  <p class="text-gray-500 mt-2">Category: <strong>{data?.category ?? 'unknown'}</strong></p>
</section>
