<script>
    import * as Card from "$lib/components/ui/card/index.js";
    import { doctors } from "$lib/mock/doctors";
</script>

<section class="px-4 md:px-8">
    <div
        class="py-8 md:py-10 mx-auto max-w-7xl px-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10"
    >
        {#each doctors as doctor (doctor.id)}
            <Card.Root
                class="overflow-hidden shadow-sm hover:shadow-md transition-shadow border-slate-100 group pt-0"
            >
                    <div class="overflow-hidden bg-slate-50">
                    <img
                        src={doctor.image}
                        alt={doctor.name}
                        class="aspect-square w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                </div>
                <Card.Footer
                    class="flex flex-col items-center md:items-start gap-1"
                >
                    <p
                        class="text-lg md:text-xl font-semibold text-[#3870FF] leading-tight"
                    >
                        {doctor.name}
                    </p>
                    <p class="text-sm md:text-base text-slate-500 line-clamp-2">
                        {doctor.bio}
                    </p>
                </Card.Footer>
            </Card.Root>
        {/each}
    </div>
</section>
