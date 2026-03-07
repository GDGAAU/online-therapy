<script>
    import logoImg from "$lib/assets/logo.png";
    import * as Card from "$lib/components/ui/card/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
</script>

<section class="py-[.5rem] md:py-[1rem]">
    <div class="mx-auto max-w-7xl px-4">
        <nav class="mb-[.5rem] md:mb-[1rem]">
            <div class="flex items-center gap-2">
                <img
                    src={logoImg}
                    alt="psychology therapy"
                    class="h-8 md:h-10 w-auto"
                />
                <span class="text-xl font-bold tracking-wider text-blue-900"
                    >online-therapy</span
                >
            </div>
        </nav>
        <div class="relative">
            <div class="w-full overflow-hidden h-[350px] md:h-[550px]">
                <img
                    src="/images/hero.png"
                    alt="patient and doctor"
                    class="w-full w-full h-full object-cover"
                />
            </div>


            <div
                class="w-[90%] md:w-full max-w-xl mx-auto relative mt-[-80px] md:mt-0 md:absolute md:-bottom-20 md:left-1/2 md:-translate-x-1/2"
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
                    <Card.Footer>
                        <Button
                            variant="outline"
                            class="w-full text-white hover:text-white bg-blue-500 hover:bg-blue-600 py-6 text-lg font-semibold rounded-xl transition-all cursor-pointer"
                            >Get Started</Button
                        >
                    </Card.Footer>
                </Card.Root>
            </div>

            
        </div>
    </div>
</section>
