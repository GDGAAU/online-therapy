<script>
  let search = "";
  let filters = ["Today", "Completed", "Pending", "Canceled", "Others"];
  let activeFilter = "Today";

  let appointments = [
    {
      id: 1,
      therapist: "Dr. Sarah Ahmed",
      time: "10:00 AM",
      status: "Pending"
    },
    {
      id: 2,
      therapist: "Dr. Daniel Kim",
      time: "2:30 PM",
      status: "Completed"
    }
  ];
</script>

<div class="min-h-screen bg-gray-50 flex justify-center">
  <div class="w-full max-w-md px-4 py-4">

    <!-- Top Icons -->
    <div class="flex justify-between items-center mb-6">
      <!-- Menu -->
      <button class="text-2xl">
        ☰
      </button>

      <!-- Notification -->
      <button class="text-2xl">
        🔔
      </button>
    </div>

    <!-- Back + Title -->
    <div class="flex items-center gap-4 mb-6">
      <button class="text-xl">
        ←
      </button>
      <h1 class="text-xl font-semibold text-[#3870FF]">
        My Appointments
      </h1>
    </div>

    <!-- Search Bar -->
    <div class="mb-6">
      <div class="flex items-center bg-white rounded-xl px-4 py-3 shadow-sm border border-gray-200">
        <span class="mr-3 text-gray-400">🔍</span>
        <input
          type="text"
          placeholder="Search for appointments"
          bind:value={search}
          class="w-full outline-none bg-transparent text-sm"
        />
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="flex gap-3 overflow-x-auto mb-6">
      {#each filters as filter}
        <button
          on:click={() => activeFilter = filter}
          class={`px-4 py-2 rounded-full text-sm whitespace-nowrap
          ${activeFilter === filter 
            ? 'bg-[#3870FF] text-white'
            : 'bg-white text-gray-600 border border-gray-200'}`}
        >
          {filter}
        </button>
      {/each}
    </div>

    <!-- Appointment Cards -->
    <div class="space-y-4">
      {#each appointments as appointment}
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="font-semibold text-gray-800">
                {appointment.therapist}
              </h2>
              <p class="text-sm text-gray-500">
                {appointment.time}
              </p>
            </div>

            <span class={`text-xs px-3 py-1 rounded-full
              ${appointment.status === "Completed" 
                ? 'bg-green-100 text-green-600'
                : appointment.status === "Pending"
                ? 'bg-yellow-100 text-yellow-600'
                : 'bg-gray-100 text-gray-600'}`}>
              {appointment.status}
            </span>
          </div>
        </div>
      {/each}
    </div>

  </div>
</div>