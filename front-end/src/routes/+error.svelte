<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { Button } from '$lib/components/ui/button';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
</script>

<svelte:head>
  <title>Error — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
  <Card className="max-w-md w-full text-center shadow-xl">
    <CardContent className="p-8 space-y-6">
    <!-- Error code -->
    <div class="text-7xl font-black text-blue-400">
      {page.status}
    </div>

    <!-- Message -->
    <div class="space-y-2">
      <h1 class="text-2xl font-bold text-gray-900">
        {page.status === 404 ? 'Page Not Found' : 'Something went wrong'}
      </h1>
      <p class="text-gray-500">
        {page.error?.message ?? 'An unexpected error occurred. Please try again.'}
      </p>
    </div>

    <!-- Actions -->
    <div class="flex gap-3 justify-center">
      <Button variant="outline" on:click={() => window.history.back()}>
        Go Back
      </Button>
      <Button on:click={() => goto('/dashboard')}>
        Go Home
      </Button>
    </div>
    </CardContent>
  </Card>
</div>
