<script>
  import { FontAwesomeIcon } from "@fortawesome/svelte-fontawesome";
  import { faBars, faBell, faUser, faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
  import { goto } from '$app/navigation'; // SvelteKit navigation

  // Filters
  let filters = ["Pediatric", "General", "Available", "Highest Rating"];
  let activeFilter = "General";

  // Search
  let searchQuery = "";

  // Doctor list
  let doctors = [
    { name: "Dr. Dawit Bekele", specialty: "General Medicine", experience: "9 years experience", available: true },
    { name: "Dr. Meron Tadesse", specialty: "General Medicine", experience: "9 years experience", available: true },
    { name: "Dr. Meron Tadesse", specialty: "General Medicine", experience: "9 years experience", available: false },
    { name: "Dr. Meron Tadesse", specialty: "Pediatric", experience: "9 years experience", available: true }
  ];

  // Filter + Search
  $: filteredDoctors = doctors
    .filter(d => {
      if (activeFilter === "Available") return true; // show all, badge indicates availability
      if (activeFilter === "Highest Rating") return true; 
      if (activeFilter === "General") return true; // General = all doctors
      return d.specialty.includes(activeFilter);
    })
    .filter(d => d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.specialty.toLowerCase().includes(searchQuery.toLowerCase()));
  
  function bookAppointment(doc) {
    if (!doc.available) {
      alert(`${doc.name} is currently unavailable.`);
      return;
    }
    alert(`Booking appointment with ${doc.name}`);
  }
</script>

<!-- HEADER -->
<div class="flex items-center justify-between px-4 py-3 bg-white">
  <FontAwesomeIcon icon={faBars} class="text-xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <FontAwesomeIcon icon={faBell} class="text-xl text-gray-700 cursor-pointer hover:text-gray-900" />
</div>

<!-- PAGE HEADER -->
<div class="flex flex-col p-4 space-y-3">
  <div class="flex flex-col items-center"> 
    <h1 class="text-xl font-bold text-[#3870FF] text-center">
      Book an Appointment
    </h1>
  </div>
  
  <!-- SEARCH INPUT -->
  <div class="flex items-center border rounded-lg px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-blue-500">
    <FontAwesomeIcon icon={faMagnifyingGlass} class="text-gray-500 mr-2" />
    <input
      type="text"
      placeholder="Search doctors..."
      class="w-full outline-none text-gray-700 placeholder-gray-400"
      bind:value={searchQuery}
    />
  </div>
</div>

<!-- FILTERS -->
<div class="flex overflow-x-auto space-x-3 px-4 py-3 scrollbar-hide">
  {#each filters as filter}
    <div
      class={`px-4 py-2 rounded-full whitespace-nowrap cursor-pointer ${
        activeFilter === filter ? "bg-[#3870FF] text-white" : "bg-gray-200 text-gray-700"
      }`}
      on:click={() => activeFilter = filter}
    >
      {filter}
    </div>
  {/each}
</div>

<!-- DOCTOR CARDS -->
<div class="flex flex-col space-y-4 px-4 pb-24">
  {#each filteredDoctors as doc}
    <div class="bg-[#ECF1FF] rounded-xl shadow p-4 flex flex-col space-y-2">
      
      <!-- Top Row -->
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <FontAwesomeIcon icon={faUser} class="text-3xl text-gray-500" />
          <div class="flex flex-col">
            <div class="font-semibold">{doc.name}</div>
            <div class="text-sm text-gray-600">{doc.specialty}</div>
            <div class="text-sm text-gray-500">{doc.experience}</div>
          </div>
        </div>

        <!-- Available Badge -->
        <div class={`px-4 py-1 min-w-[90px] text-center rounded-full text-sm font-semibold ${
          doc.available 
            ? 'bg-green-600 text-white'  // uniform green
            : 'bg-red-500 text-white'    // uniform red
        }`}>
          {doc.available ? 'Available' : 'Unavailable'}
        </div>
      </div>

      <!-- Bottom Row: Book Button -->
      <div class="flex space-x-3 mt-2">
        <button
          class={`flex-1 px-4 py-2 rounded cursor-pointer ${
            doc.available
              ? "bg-gradient-to-r from-[#38B7FF] to-[#1C92FF] text-white"
              : "border border-[#38B7FF] text-[#38B7FF]"
          }`}
          on:click={() => bookAppointment(doc)}
        >
          Book Appointment
        </button>
      </div>
    </div>
  {/each}
</div>

<style>
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>