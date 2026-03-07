<script lang="ts">
  /**
   * /login — Login page
   *
   * Stack:
   * - superforms for form state management
   * - zod for validation
   * - sonner toast for error feedback
   * - authApi for the actual request
   */
  import { superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import { Eye, EyeOff, Loader2 } from 'lucide-svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { loginSchema } from '$lib/schemas';
  import { login } from '$lib/stores/auth';
  import { ApiError } from '$lib/api';

  // superforms — client-only usage (no load function needed for public pages)
  const { form, errors, enhance, submitting } = superForm(
    { email: '', password: '' },
    {
      validators: zod(loginSchema as any),
      SPA: true, // client-side only
      async onUpdate({ form }) {
        if (!form.valid) return;

        try {
          await login(form.data.email, form.data.password);
          toast.success('Welcome back!');
        } catch (err) {
          if (err instanceof ApiError) {
            if (err.code === 'ACCOUNT_NOT_ACTIVATED') {
              toast.error('Account not activated. Please check your email.', {
                action: {
                  label: 'Resend email',
                  onClick: () => goto('/resend-activation')
                }
              });
            } else {
              toast.error(err.message);
            }
          } else {
            toast.error('An unexpected error occurred. Please try again.');
          }
        }
      }
    }
  );

  let showPassword = false;
</script>

<svelte:head>
  <title>Log In — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-linear-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-12">
  <div class="w-full max-w-md">
    <Card className="overflow-hidden border-none shadow-xl">
  <div class="bg-linear-to-r from-blue-500 to-indigo-500 p-6 text-white">
        <a href="/" class="flex items-center gap-2 text-white/80 hover:text-white">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          <span class="text-sm">Back to home</span>
        </a>
        <h1 class="mt-4 text-2xl font-semibold">Welcome back</h1>
        <p class="text-sm text-white/80">Log in to continue your therapy journey.</p>
      </div>
      <CardContent className="space-y-6 px-6 py-8">
        <form use:enhance method="POST" class="space-y-4">
          <div class="space-y-1">
            <Label forValue="email">Email *</Label>
            <Input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              bind:value={$form.email}
              className={$errors.email ? 'border-red-400' : 'border-gray-200'}
              placeholder="you@example.com"
            />
            {#if $errors.email}
              <p class="text-red-500 text-xs mt-1">{$errors.email}</p>
            {/if}
          </div>

          <div class="space-y-1">
            <Label forValue="password">Password *</Label>
            <div class="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autocomplete="current-password"
                bind:value={$form.password}
                className={'pr-11 ' + ($errors.password ? 'border-red-400' : 'border-gray-200')}
                placeholder="Enter your password"
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                on:click={() => (showPassword = !showPassword)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {#if showPassword}
                  <EyeOff size={18} />
                {:else}
                  <Eye size={18} />
                {/if}
              </Button>
            </div>
            {#if $errors.password}
              <p class="text-red-500 text-xs mt-1">{$errors.password}</p>
            {/if}
          </div>

          <div class="flex items-center justify-between text-sm text-gray-500">
            <label class="flex items-center gap-2">
              <input type="checkbox" class="h-4 w-4 rounded border-gray-300 text-blue-500" />
              Remember me
            </label>
            <a href="/forgot-password" class="text-blue-500 hover:underline">Forgot Password?</a>
          </div>

          <Button type="submit" disabled={$submitting} className="w-full bg-blue-500 text-white shadow-md">
            {#if $submitting}
              <Loader2 size={18} class="animate-spin" /> Logging in…
            {:else}
              Login
            {/if}
          </Button>
        </form>

        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-200"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-3 bg-white text-gray-500">OR</span>
          </div>
        </div>

        <Button type="button" variant="outline" className="w-full justify-center gap-3">
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Login with Google
        </Button>
      </CardContent>
    </Card>

    <p class="text-center text-gray-500 text-sm mt-6">
      New Patient?
      <a href="/signup" class="text-blue-500 font-medium hover:underline">Create account</a>
    </p>
  </div>
</div>
