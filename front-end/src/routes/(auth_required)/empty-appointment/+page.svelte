<script>
  import { FontAwesomeIcon } from "@fortawesome/svelte-fontawesome";
  import { faBars, faBell, faAngleLeft } from "@fortawesome/free-solid-svg-icons";
  import { goto } from '$app/navigation';
  import { Button } from '$lib/components/ui/button';
  import emptyStateImage from '$lib/assets/emptyState.png';

  // Function to navigate to book-appointment page
  function goToBookAppointment() {
    goto('/book-appointment');
  }
</script>

<!-- HEADER: Menu + Notification -->
<div class="flex items-center justify-between px-4 py-3 bg-white shadow">
  <FontAwesomeIcon icon={faBars} class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <FontAwesomeIcon icon={faBell} class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" />
</div>

<!-- PAGE HEADER: Back + Title -->
<div class="flex items-center justify-between px-4 py-3 bg-white">
  <FontAwesomeIcon icon={faAngleLeft} class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <h1 class="text-2xl font-bold text-[#3870FF] text-center flex-1">My Appointments</h1>
  <div class="w-6"></div> <!-- spacer so title stays centered -->
</div>

<!-- EMPTY STATE CONTENT -->
<div class="flex flex-col items-center justify-center h-[60vh] text-center px-4 space-y-6">
  
  <!-- Centered Image -->
  <img 
    src={emptyStateImage} 
    alt="No Appointments" 
    class="w-48 h-48 object-contain" 
  />

  <!-- Empty State Text -->
  <p class="text-gray-500 text-base max-w-xs mb-4">
    Looks like you don’t have any appointments yet. Tap "Book Now" to get started.
  </p>

  <!-- Button to Book Appointment -->
  <Button
    className="px-4 py-2 rounded bg-gradient-to-r from-[#38B7FF] to-[#1C92FF] text-white"
    on:click={goToBookAppointment}
  >
    <span class="text-xl font-bold">+</span>
    <span>Book Now</span>
  </Button>

</div>
