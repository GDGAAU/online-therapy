<script>
    import * as Card from "$lib/components/ui/card";
    import {Button} from  "$lib/components/ui/button"
</script>

<section>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 my-4 px-6">
        <Card.Root class="px-6 shadow-lg bg-[#ECF1FF] mx-2.5 my-4 ">
            <div class="flex gap-4 text-center items-center">
                <i class="fa-solid fa-users text-xl"></i>
                <p class="font-semibold text-xl">Current Queue status</p>
            </div>

            <div class="bg-[#809CFF47] rounded-sm p-6 space-y-3 text-[16px]">
                <div class="flex justify-between">
                    <div class="text-[#878787]">Your position</div>
                    <div class="font-semibold">#2</div>
                </div>
                <div class="flex justify-between">
                    <div class="text-[#878787]">Department</div>
                    <div class="font-semibold">21 mins</div>
                </div>
                <div class="flex justify-between">
                    <div class="text-[#878787]">Status</div>
                    <div
                        class="bg-[#FBBC0440] text-[#FBBC04] px-3 py-0.5 font-semibold rounded-sm"
                    >
                        WAITING
                    </div>
                </div>
            </div>

            <div class="bg-[#D9D9D9] text-center px-3.5 py-4 rounded-xl ">
                <p class="text-[#878787] ">Estimated Call time</p>
                <p class="font-semibold">2:45 AM</p>
            </div>
        </Card.Root>



        <Card.Root class="px-6 shadow-lg bg-[#ECF1FF] mx-2.5 my-4 ">
            <div>

                <div class="flex gap-4 text-center items-center">
                    <i class="fa-solid fa-pills text-2xl text-[#AF52DE]"></i>
                    <p class="font-semibold text-xl">Today's Medications</p>
                </div>

                <div class="flex justify-between  border border-[#656565] rounded-xl my-3.5 items-center p-2">
                    <div class="space-y-1">
                        <p class="font-semibold">abcdefg</p>
                        <p class="text-[#878787]">8:00 AM</p>
                    </div>
                    <div class="bg-[#34A85340] text-[#34A853] px-3 font-semibold rounded-sm">
                        TAKEN
                    </div>
                </div>

                <div class="flex justify-between  border border-[#656565] rounded-xl my-3.5 items-center p-2">

                    <div class="space-y-1">
                        <p class="font-semibold">abcdefg</p>
                        <p class="text-[#878787]">8:00 AM</p>
                    </div>
                    <div  class="bg-[#FBBC0440] text-[#FBBC04] px-3 py-0.5 font-semibold rounded-sm">
                        WAITING
                    </div>
                </div>


                <Button class="bg-linear-to-r from-[#3870FF] to-[#38B7FF] w-full text-xl py-6  cursor-pointer">
                    <i class="fa-solid fa-plus"></i>
                    <p>Set Reminder </p>
                </Button>

            </div>
        </Card.Root>




        <Card.Root class="px-6 shadow-lg bg-[#ECF1FF] mx-2.5 my-4 ">

            <div class="flex items-center justify-between gap-3">

                <i class="fa-solid fa-calendar-check text-xl"></i>
                <p class="font-semibold"> Upcoming Appointments</p>

                <Button class="bg-linear-to-r from-[#3870FF] to-[#38B7FF]   py-5 cursor-pointer">
                    <i class="fa-solid fa-plus"></i>
                    <p> Book new</p>
                </Button>
            </div>

            <div class="border border-[#656565] rounded-xl shadow-xl  p-3">
                <div  class="bg-[#809CFF]  px-3 py-0.5 font-semibold rounded-sm w-max text-white">
                    Upcoming
                </div>

                <div class="flex items-center justify-between py-3">
                    <div>
                        <p class="font-semibold">Dr. Dawit Bekele</p>
                        <p class="text-[#656565]">Psychologist . CheckUp</p>
                    </div>
                    <div  class="bg-[#FBBC0440] text-[#FBBC04] px-3 py-0.5 font-semibold rounded-sm">
                        Pending 
                    </div>
                </div>
                <div class="flex items-center gap-2" >
                    <i class="fa-regular fa-clock"></i>
                    <p class="text-[#656565]">  04-09-2025 at 2:30 PM </p>
                </div> 

                <Button class="mt-2 p-1.5 text-[#38B7FF] border border-[#3870FF] text-xl py-5 bg-[#ECF1FF] w-full rounded-xl hover:bg-[#38B7FF] hover:text-white cursor-pointer">
                    Cancel
                </Button>
                
            </div>

        </Card.Root>


 

        <Card.Root class="px-6 shadow-lg bg-[#ECF1FF] mx-2.5 my-4 ">

            <div class="flex items-center gap-3">
                <i class="fa-solid fa-hand-holding-heart  text-2xl"></i>
                <p class="font-semibold text-xl"> Daily Wellness Tips</p>
            </div>
            <p class="font-medium">
                Stay hydrated! Aim for 8 glasses of water throughout the day to maintain optimal health
            </p>

            <Button class="bg-linear-to-r from-[#3870FF] to-[#38B7FF] w-full text-xl py-6  cursor-pointer">
                <p>More Tips </p>
            </Button>
        </Card.Root>





        <Card.Root class="px-6 shadow-lg bg-[#ECF1FF] mx-2.5 my-4 ">

            <div class="flex items-center gap-3">
                <i class="fa-solid fa-comment  text-2xl"></i>
                <p class="font-semibold text-xl"> AI chat Assistant</p>
            </div>
            <p class="font-medium">
                Ask me about appointments, medications, or both Health questions.
            </p>

            <Button class="bg-linear-to-r from-[#3870FF] to-[#38B7FF] w-full text-xl py-6  cursor-pointer">
                <i class="fa-solid fa-comment  text-2xl"></i>
                <p>Start Chat </p>
            </Button>
        </Card.Root>
    </div>
</section>


        
