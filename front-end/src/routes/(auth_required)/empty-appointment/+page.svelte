<script lang="ts">
  import { goto } from '$app/navigation';
  import { FontAwesomeIcon } from "@fortawesome/svelte-fontawesome";
  import { faBars, faBell, faAngleLeft } from "@fortawesome/free-solid-svg-icons";
  import emptyStateImage from '$lib/assets/emptyState.png';

  // Function to navigate to book-appointment page
  function goToBookAppointment() {
    goto('/book-appointment');
  }
</script>

<!-- PAGE HEADER-->
<div class="flex items-center justify-between px-4 py-3 bg-white">
  <FontAwesomeIcon icon={faAngleLeft} class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <h1 class="text-2xl font-bold text-[#3870FF] text-center flex-1">My Appointments</h1>
  <div class="w-6"></div> 
</div>

<!-- EMPTY STATE CONTENT -->
<div class="flex flex-col items-center justify-center h-[60vh] text-center px-4 space-y-6">
  
  <!-- Centered Image -->
  <img 
    src={emptyStateImage} 
    alt="No Appointments" 
    class="w-172 h-102 md:w-96 md:h-96 object-contain" 
  />

  <!-- Empty State Text -->
  <p class="text-gray-500 text-base max-w-xs mb-4">
    Looks like you don’t have any appointments yet. Tap "Book Now" to get started.
  </p>

  <!-- Button to Book Appointment -->
  <button
    on:click={goToBookAppointment}
    class="inline-flex items-center justify-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-[#38B7FF] to-[#3870FF] text-white font-medium transition-opacity hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
  >
    <span class="text-xl font-bold mr-2">+</span>
    <span>Book Now</span>
  </button>

</div>