<script>
    import { authStore } from "$lib/stores/auth";

</script>

<section class="px-4 md:px-8  " >
    <div class="md:pt-24 pt-32 mx-auto max-w-7xl px-4">
        <!-- logged user name -->
        <h1  class="text-[#3870FF] text-2xl md:text-4xl font-bold md:text-center mb-2 text-balance">Welcome Back {$authStore.user?.first_name ?? 'there'}</h1>
        <p class="mb-2 text-base md:text-lg leading-relaxed text-slate-600 text-pretty md:text-center">Here is your overview for today</p>
    </div>
</section>

