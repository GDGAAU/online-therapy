<script>
    import * as Card from "$lib/components/ui/card";
</script>

<section class="px-4 md:px-8">
    <div class="md:py-4 py-1 mx-auto max-w-7xl px-2">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            <Card.Root class="bg-[#ECF1FF] px-3 md:px-6 shadow-xl">
                <div class="flex gap-3">
                    <div>
                        <i
                            class="fa-regular fa-calendar-check text-[#3870FF] text-2xl"
                        ></i>
                    </div>

                    <div class="flex flex-col items-start justify-center">
                        <p
                            class="text-sm md:text-base text-slate-600 leading-tight mb-2"
                        >
                            Next appointment
                        </p>
                        <p class="font-bold">24-10-25</p>
                    </div>
                </div>
            </Card.Root>

            <Card.Root class="bg-[#ECF1FF] px-3  md:px-6 shadow-xl">
                <div class="flex gap-3">
                    <div>
                        <i class="fa-solid fa-users text-2xl text-[#34C759]"
                        ></i>
                    </div>
                    <div class="flex flex-col items-start justify-center">
                        <p
                            class="text-sm md:text-base text-slate-600 leading-tight mb-2"
                        >
                            Queue position
                        </p>
                      <p class="font-bold">#2</p>
                    </div>
                </div>
            </Card.Root>

            <Card.Root class="bg-[#ECF1FF] px-3 md:px-6 shadow-xl">
                <div class="flex gap-3">
                    <div>
                        <i class="fa-regular fa-clock text-2xl text-[#FFCC00]"
                        ></i>
                    </div>
                    <div class="flex flex-col items-start justify-center">
                        <p
                            class="text-sm md:text-base text-slate-600 leading-tight mb-2"
                        >
                            Est. Wait Time
                        </p>
                        <p class="font-bold">10-15 min</p>
                    </div>
                </div>
            </Card.Root>

            <Card.Root class="bg-[#ECF1FF] px-3 md:px-6 shadow-xl">
                <div class="flex gap-3">
                    <div>
                        <i class="fa-solid fa-pills text-2xl text-[#AF52DE]"
                        ></i>
                    </div>
                    <div class="flex flex-col items-start justify-center">
                        <p
                            class="text-sm md:text-base text-slate-600 leading-tight mb-2"
                        >
                            Medications
                        </p>
                       <p class="font-bold">2 Active</p>
                    </div>
                </div>
            </Card.Root>
        </div>
    </div>
</section>