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
            class="py-8 md:py-10 mx-auto max-w-7xl px-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10"
        >
            {#each blogs as blog (blog.id)}
                <Card.Root
                    class="overflow-hidden shadow-sm hover:shadow-md transition-shadow border-slate-100 group"
                >
                    <div class="overflow-hidden bg-slate-50">
                        <img
                            src={blog.image}
                            alt={blog.title}
                            class="aspect-square w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                    </div>
                    <h1>
                        {blog.title}
                    </h1>
                    <p
                        class="text-lg md:text-xl font-semibold text-[#3870FF] leading-tight"
                    >
                        {blog.description}
                    </p>
                    <Card.Footer></Card.Footer>
                </Card.Root>
            {/each}
        </div>
    </div>
</section>
