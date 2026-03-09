<script>
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { authStore } from "$lib/stores/auth";
</script>

<section class="py-2 md:py-4">
    <div class="mx-auto max-w-7xl px-4">
        <div class="relative">
            <div class="w-full overflow-hidden h-88 md:h-136">
                <img
                    src="/images/hero.png"
                    alt="patient and doctor"
                    class="w-full h-full object-cover"
                />
            </div>


            <div
                class="w-[90%] md:w-full max-w-xl mx-auto relative -mt-20 md:mt-0 md:absolute md:-bottom-20 md:left-1/2 md:-translate-x-1/2 bg-white rounded-xl"
            >
                <Card.Root
                    class="shadow-2xl border-none p-4 md:p-6 text-center"
                >
                    <Card.Header>
                        <Card.Title
                            class="text-2xl md:text-4xl font-bold text-[#3870FF] text-balance"
                            >Welcome to online-therapy</Card.Title
                        >
                    </Card.Header>
                    <Card.Content>
                        <p
                            class="text-base md:text-lg leading-relaxed text-slate-600 text-pretty"
                        >
                            Your digital bridge to accessible mental health
                            support where you book therapy sessions, join secure
                            virtual appointments, manage payments, and access
                            trusted resources all in one secure platform.
                        </p>
                    </Card.Content>
                    {#if !$authStore.user}
                        <Card.Footer>
                            <div class="flex flex-col gap-3 w-full sm:flex-row sm:justify-center">
                                <a href="/signup" class="w-full sm:w-auto">
                                    <Button
                                        variant="outline"
                                        class="w-full text-white hover:text-white bg-blue-500 hover:bg-blue-600 py-6 text-lg font-semibold rounded-xl transition-all cursor-pointer"
                                    >
                                        Get Started
                                    </Button>
                                </a>
                                <a href="/login" class="w-full sm:w-auto">
                                    <Button
                                        variant="outline"
                                        class="w-full text-blue-600 hover:text-white border-blue-500 hover:bg-blue-500 py-6 text-lg font-semibold rounded-xl transition-all cursor-pointer"
                                    >
                                        Log In
                                    </Button>
                                </a>
                            </div>
                        </Card.Footer>
                    {/if}
                </Card.Root>
            </div>

            
        </div>
    </div>
</section>
