<script>
    import { Button } from "$lib/components/ui/button";
    let { color, bgColor,OnToggle} = $props();
    

    
</script>

<section
    class="px-4 shadow-sm fixed top-0 left-0 right-0 z-1000"
    style="background-color:{bgColor} ;"
>
    <nav class="flex justify-between md:py-4 py-5 mx-auto max-w-7xl px-4">
        <Button
            class="hover:bg-gray-100 active:bg-gray-200 font-semibold rounded-xl transition-all cursor-pointer px-3 py-3 border-0 bg-transparent shadow-none"
            onclick={OnToggle}
            ><i
                class="fa-solid fa-bars text-2xl md:text-xl"
                style="color:{color}"
            ></i></Button

        >
        <Button
            class= "shadow-none hover:bg-gray-100 active:bg-gray-200 font-semibold rounded-xl transition-all cursor-pointer px-3 py-3 border-0 bg-transparent"
            ><i
                class="fa-regular fa-bell text-2xl md:text-xl"
                style="color:{color}"
            ></i></Button
        >
    </nav>
</section>
