<script>
  import { FontAwesomeIcon } from "@fortawesome/svelte-fontawesome";
  import { faBars, faBell, faAngleLeft, faClock, faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
  import { goto } from '$app/navigation';
  import { onMount } from "svelte";

  // Filters
  let filters = ["All","Today", "Completed", "Pending", "Cancelled"];
  let activeFilter = "All";

  // Search
  let searchQuery = "";

  // Appointments
  let appointments = [
    {
      tag: "Upcoming",
      doctor: "Dr. Dawit Bekele",
      status: "Pending",
      type: "Psychologist.Check-up",
      time: "04-09-2025 at 2:30 PM",
      buttons: ["Reschedule", "Cancel"],
      tagColor: "bg-[#809CFF] text-white",
      buttonColor: "bg-gradient-to-r from-[#38B7FF] to-[#38B7FF] text-white"
    },
    {
      tag: "Today",
      doctor: "Dr. Hemen Bekele",
      status: "Confirmed",
      type: "Psychologist.Check-up",
      time: "04-09-2025 at 2:30 PM",
      buttons: ["View Queue"],
      tagColor: "bg-[#809CFF] text-white",
      buttonColor: "bg-gradient-to-r from-[#38B7FF] to-[#38B7FF] text-white"
    },
    {
      tag: "Upcoming",
      doctor: "Dr. Dawit Bekele",
      status: "Confirmed",
      type: "Psychologist.Check-up",
      time: "04-09-2025 at 2:30 PM",
      buttons: ["Reschedule", "Cancel"],
      tagColor: "bg-[#809CFF] text-white",
      buttonColor: "bg-gradient-to-r from-[#38B7FF] to-[#38B7FF] text-white"
    },
    {
      tag: "Completed",
      doctor: "Dr. Dawit Bekele",
      status: "",
      type: "Psychologist.Check-up",
      time: "04-09-2025 at 2:30 PM",
      buttons: ["View Medical Record"],
      tagColor: "bg-[#809CFF] text-white",
      buttonColor: "bg-gradient-to-r from-[#38B7FF] to-[#38B7FF] text-white"
    },
    {
      tag: "Upcoming",
      doctor: "Dr. Dawit Bekele",
      status: "Cancelled",
      type: "Psychologist.Check-up",
      time: "04-09-2025 at 2:30 PM",
      buttons: ["Book Again"],
      tagColor: "bg-[#809CFF] text-white",
      buttonColor: "bg-gradient-to-r from-[#38B7FF] to-[#38B7FF] text-white"
    }
  ];

  // FILTER + SEARCH COMBINED
  $: filteredAppointments = appointments
    .filter(a =>
      activeFilter === "All" ||
      a.tag === activeFilter ||
      a.status === activeFilter
    )
    .filter(a =>
      a.doctor.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.type && a.type.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (a.status && a.status.toLowerCase().includes(searchQuery.toLowerCase()))
    );

  // Modal state
  let showModal = false;
  let modalMessage = "";

  function handleCancel(appt) {
    modalMessage = `Are you sure you want to cancel ${appt.doctor}'s appointment?`;
    showModal = true;
  }

  function handleConfirmCancel() {
    showModal = false;
  }

  function handleButtonClick(btn, appt) {
    if (btn === "Cancel") {
      handleCancel(appt);
    } else {
      alert(`${btn} clicked for ${appt.doctor}`);
    }
  }

  // SvelteKit navigation to Book Appointment page
  function goToBookPage() {
    goto('/book-appointment');
  }
</script>

<!--HEADER -->
<div class="flex items-center justify-between px-4 py-3 bg-white">
  <FontAwesomeIcon icon={faBars} class="text-xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <FontAwesomeIcon icon={faBell} class="text-xl text-gray-700 cursor-pointer hover:text-gray-900" />
</div>

<div class="flex items-center justify-between p-4">
  <FontAwesomeIcon icon={faAngleLeft} class="text-2xl text-gray-700 cursor-pointer hover:text-gray-900" />
  <h1 class="text-xl font-bold text-[#3870FF] text-center flex-1">
    My Appointments
  </h1>
</div>

<!-- SEARCH BOX -->
<div class="px-4 mb-4">
  <div class="flex items-center border rounded-lg px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-blue-500">
    <FontAwesomeIcon icon={faMagnifyingGlass} class="text-gray-500 mr-2" />
    <input
      type="text"
      placeholder="Search for appointments"
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

<!-- APPOINTMENT CARDS -->
<div class="flex flex-col space-y-4 px-4 pb-24">
  {#each filteredAppointments as appt}
    <div class="bg-[#ECF1FF] rounded-xl shadow p-4 space-y-2">
      
      <div class="flex justify-start">
        <div class={`px-3 py-1 rounded-full text-sm font-semibold ${appt.tagColor}`}>
          {appt.tag}
        </div>
      </div>

      <div class="flex justify-between items-center mt-2">
        <div class="font-semibold">{appt.doctor}</div>

        {#if appt.status} 
          <div
            class="px-3 py-1 rounded-full text-sm font-medium"
            style="
              background-color: 
                {appt.status === 'Confirmed' ? '#34A85340' :
                 appt.status === 'Pending' ? '#FBBC0440' :
                 appt.status === 'Cancelled' ? '#EA433540' :
                 '#CCCCCC'};
              color: 
                {appt.status === 'Confirmed' ? '#34A853' :
                 appt.status === 'Pending' ? '#FBBC04' :
                 appt.status === 'Cancelled' ? '#EA4335' :
                 '#333333'};
            "
          >
            {appt.status}
          </div>
        {/if}
      </div>

      {#if appt.type} 
        <div class="text-sm text-gray-600 mt-1">
          {appt.type}
        </div>
      {/if}

      <div class="flex items-center text-gray-500 text-sm">
        <FontAwesomeIcon icon={faClock} class="mr-2" /> {appt.time}
      </div>

      <div class="flex space-x-3 mt-2">
        {#each appt.buttons as btn}
          <button
            class={`flex-1 px-4 py-2 rounded cursor-pointer ${
              btn === "Cancel"
                ? "border border-[#38B7FF] text-[#38B7FF]"
                : "bg-gradient-to-r from-[#38B7FF] to-[#1C92FF] text-white"
            }`}
            on:click={() => handleButtonClick(btn, appt)}
          >
            {btn}
          </button>
        {/each}
      </div>

    </div>
  {/each}
</div>

<!-- PLUS BUTTON -->
<div class="fixed bottom-6 right-6">
  <button
    class="flex items-center space-x-2 bg-blue-500 text-white px-4 py-3 rounded-full shadow-lg"
    on:click={goToBookPage} 
  >
    <span class="text-xl font-bold">+</span>
    <span>Book Now</span>
  </button>
</div>

<!-- CANCEL CONFIRM MODAL -->
{#if showModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 space-y-4 w-80">
      <p class="text-gray-700">{modalMessage}</p>
      <div class="flex justify-end space-x-3">
        <button class="px-4 py-2 rounded border border-gray-300 text-gray-700" on:click={() => showModal = false}>
          No
        </button>
        <button class="px-4 py-2 rounded bg-gradient-to-r from-[#38B7FF] to-[#1C92FF] text-white" on:click={handleConfirmCancel}>
          Yes
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>