<script>
    import * as Card from "$lib/components/ui/card/index.js";
    import { blogs } from "$lib/mock/blogs";
    import { Button } from "$lib/components/ui/button/index.js";
</script>

<section class="px-4 md:px-8">
    <div class="mx-auto max-w-7xl py-8 md:py-10">
        <h1
            class="text-[#3870FF] text-2xl md:text-4xl font-bold text-center mb-6"
        >
            Our Latest Blogs
        </h1>
        <div
            class="py-8 md:py-10 mx-auto max-w-7xl px-4 grid grid-cols-1 md:grid-cols-2 gap-10"
        >
            {#each blogs as blog (blog.id)}
                <Card.Root
                    class="overflow-hidden shadow-sm hover:shadow-md transition-shadow border-slate-100 group pt-0"
                >
                    <div class="overflow-hidden rounded-t-2xl">
                        <img
                            src={blog.image}
                            alt={blog.title}
                            class="aspect-[16/9] w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold px-4 mb-2 text-balance">
                            {blog.title}
                        </h3>
                        <p
                            class="text-base md:text-lg leading-relaxed text-slate-600 text-pretty px-4 line-clamp-2"
                        >
                            {blog.description}
                        </p>
                        <div class="px-4">
                            <Button
                                variant="outline"
                                class="text-md py-5 my-6 rounded-full border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white cursor-pointer"
                            >
                                Learn More <i
                                    class="fa-solid fa-arrow-right ml-2"
                                ></i>
                            </Button>
                        </div>
                    </div>
                </Card.Root>
            {/each}
        </div>
    </div>
</section>
