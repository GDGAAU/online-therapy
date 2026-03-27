<script lang="ts">
  interface Props {
    data: { slug: string } | undefined;
  }

  let { data }: Props = $props();
</script>

<svelte:head>
  <title>Post — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-3xl p-6">
  <h1 class="text-2xl font-semibold text-gray-900">Post</h1>
  <p class="text-gray-500 mt-2">Post content for <strong>{data?.slug ?? 'unknown'}</strong> will render here.</p>
</section>
