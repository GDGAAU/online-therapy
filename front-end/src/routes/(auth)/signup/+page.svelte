<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import Icon from '$lib/components/icons/Icon.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Card } from '$lib/components/ui/card';
  import { CardContent } from '$lib/components/ui/card-content';
  import { registerSchema } from '$lib/schemas';
  import { authApi, ApiError } from '$lib/api';
  import { loginWithGoogle } from '$lib/stores/auth';
  import { requestGoogleIdToken } from '$lib/auth/google';
  import { env } from '$env/dynamic/public';

  const { form, errors, enhance, submitting } = superForm(
    {
      full_name: '',
      date_of_birth: '',
      phone_number: '',
      email: '',
      password: '',
      re_password: ''
    },
    {
      validators: zod(registerSchema as any),
      SPA: true,
      async onUpdate({ form }) {
        if (!form.valid) return;

        try {
          await authApi.register({
            full_name: form.data.full_name,
            date_of_birth: form.data.date_of_birth,
            phone_number: form.data.phone_number,
            email: form.data.email,
            password: form.data.password,
            re_password: form.data.re_password
          });

          registered = true;
          toast.success('Account created! Please check your email to verify.');
        } catch (err) {
          toast.error(err instanceof ApiError ? err.message : 'Registration failed. Please try again.');
        }
      }
    }
  );

  let showPassword = $state(false);
  let registered = $state(false);
  let isGoogleLoading = $state(false);

  async function handleGoogleSignup() {
    if (!env.PUBLIC_GOOGLE_CLIENT_ID) {
      toast.error('Google sign-up is not configured for this environment.');
      return;
    }

    isGoogleLoading = true;
    try {
      const idToken = await requestGoogleIdToken(env.PUBLIC_GOOGLE_CLIENT_ID);
      await loginWithGoogle(idToken);
      toast.success('Signed in with Google.');
    } catch (err) {
      if (err instanceof ApiError) {
        toast.error(err.message);
      } else {
        toast.error(err instanceof Error ? err.message : 'Google sign-up failed. Please try again.');
      }
    } finally {
      isGoogleLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Create Account — Online Therapy</title>
</svelte:head>

<div class="min-h-screen bg-linear-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 py-12">
  <div class="w-full max-w-md">
    {#if registered}
      <!-- Success State -->
      <Card className="text-center">
        <CardContent className="space-y-4">
        <div class="flex justify-center">
          <Icon name="check-circle" class="text-green-500" size={56} />
        </div>
        <h2 class="text-xl font-bold text-gray-900">Check your email!</h2>
        <p class="text-gray-500">
          We've sent a verification link to <strong>{$form.email}</strong>.
          Click the link to activate your account.
        </p>
        <Button className="w-full" onclick={() => goto('/login')}>
          Back to Login
        </Button>
        </CardContent>
      </Card>
    {:else}
      <Card className="overflow-hidden border-none shadow-xl">
        <div class="bg-linear-to-r from-blue-500 to-indigo-500 p-6 text-white">
          <a href="/" class="flex items-center gap-2 text-white/80 hover:text-white">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            <span class="text-sm">Back to home</span>
          </a>
          <h1 class="mt-4 text-2xl font-semibold">Create your account</h1>
          <p class="text-sm text-white/80">Join online-therapy and start feeling better.</p>
        </div>
        <CardContent className="space-y-4 px-6 py-8">
          <form use:enhance method="POST" class="space-y-4">
            <div class="space-y-1">
              <Label forValue="full_name">Full Name *</Label>
              <Input
                id="full_name"
                type="text"
                bind:value={$form.full_name}
                className={$errors.full_name ? 'border-red-400' : 'border-gray-200'}
                placeholder="Jane Doe"
              />
              {#if $errors.full_name}
                <p class="text-red-500 text-xs">{$errors.full_name}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label forValue="date_of_birth">Date of Birth *</Label>
              <Input
                id="date_of_birth"
                type="date"
                bind:value={$form.date_of_birth}
                className={$errors.date_of_birth ? 'border-red-400' : 'border-gray-200'}
              />
              {#if $errors.date_of_birth}
                <p class="text-red-500 text-xs">{$errors.date_of_birth}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label forValue="phone_number">Phone Number *</Label>
              <Input
                id="phone_number"
                type="tel"
                bind:value={$form.phone_number}
                className={$errors.phone_number ? 'border-red-400' : 'border-gray-200'}
                placeholder="(123) 456-7890"
              />
              {#if $errors.phone_number}
                <p class="text-red-500 text-xs">{$errors.phone_number}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label forValue="email">Email *</Label>
              <Input
                id="email"
                type="email"
                bind:value={$form.email}
                className={$errors.email ? 'border-red-400' : 'border-gray-200'}
                placeholder="you@example.com"
              />
              {#if $errors.email}
                <p class="text-red-500 text-xs">{$errors.email}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label forValue="password">Password *</Label>
              <div class="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  bind:value={$form.password}
                  className={
                    'pr-11 ' + ($errors.password ? 'border-red-400' : 'border-gray-200')
                  }
                  placeholder="Create a strong password"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onclick={() => (showPassword = !showPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400"
                >
                  {#if showPassword}
                    <Icon name="eye-slash" size={18} />
                  {:else}
                      <Icon name="eye" size={18} />
                  {/if}
                </Button>
              </div>
              {#if $errors.password}
                <p class="text-red-500 text-xs">{$errors.password}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label forValue="re_password">Confirm Password *</Label>
              <Input
                id="re_password"
                type="password"
                bind:value={$form.re_password}
                className={$errors.re_password ? 'border-red-400' : 'border-gray-200'}
                placeholder="Confirm your password"
              />
              {#if $errors.re_password}
                <p class="text-red-500 text-xs">{$errors.re_password}</p>
              {/if}
            </div>

            <Button type="submit" disabled={$submitting} className="w-full bg-blue-500 text-white">
              {#if $submitting}
                <Icon name="spinner" class="animate-spin" size={18} /> Creating account…
              {:else}
                Sign up
              {/if}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div class="my-6 flex items-center gap-3 text-xs text-gray-400">
        <div class="h-px flex-1 bg-gray-200"></div>
        <span>OR</span>
        <div class="h-px flex-1 bg-gray-200"></div>
      </div>

      <Button
        type="button"
        variant="outline"
        className="w-full justify-center gap-3"
        onclick={handleGoogleSignup}
        disabled={isGoogleLoading}
      >
        <svg width="18" height="18" viewBox="0 0 24 24">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        {isGoogleLoading ? 'Connecting Google…' : 'Sign up with Google'}
      </Button>

      <p class="text-center text-gray-500 text-sm mt-6">
        Already have an account?
        <a href="/login" class="text-blue-500 font-medium hover:underline">Login</a>
      </p>
    {/if}
  </div>
</div>
