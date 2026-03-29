<script lang="ts">
  interface AdminModule {
    id: string;
    title: string;
    description: string;
    route: string;
    icon: string;
    metric: string;
    metricLabel: string;
  }

  const modules: AdminModule[] = [
    {
      id: 'therapist-mgmt',
      title: 'Therapist Management',
      description: 'Create/delete therapists and enforce RBAC policy for staff therapist accounts.',
      route: '/admin-dashboard/therapist-management',
      icon: 'fa-user-doctor',
      metric: '24',
      metricLabel: 'total therapists'
    },
    {
      id: 'user-mgmt',
      title: 'User Management',
      description: 'Review user lifecycle, activation state, suspensions, and account hygiene.',
      route: '/admin-dashboard/user-management',
      icon: 'fa-users',
      metric: '1,283',
      metricLabel: 'registered users'
    },
    {
      id: 'appointment-ops',
      title: 'Appointment Operations',
      description: 'Monitor cancellations, no-shows, and scheduling conflicts across the platform.',
      route: '/admin-dashboard/appointment-operations',
      icon: 'fa-calendar-check',
      metric: '312',
      metricLabel: 'monthly sessions'
    },
    {
      id: 'reports',
      title: 'Reports & Audits',
      description: 'Inspect system logs, operational KPIs, and clinical workload distribution.',
      route: '/admin-dashboard/reports',
      icon: 'fa-chart-line',
      metric: '8',
      metricLabel: 'scheduled reports'
    },
    {
      id: 'settings',
      title: 'Platform Settings',
      description: 'Configure service-level policies, communication templates, and integrations.',
      route: '/admin-dashboard/platform-settings',
      icon: 'fa-gear',
      metric: '12',
      metricLabel: 'config groups'
    }
  ];
</script>

<svelte:head>
  <title>Admin Dashboard — Online Therapy</title>
</svelte:head>

<section class="mx-auto max-w-7xl space-y-6 p-4 pb-10 sm:p-6">
  <header class="rounded-2xl border border-blue-100 bg-linear-to-r from-white to-blue-50 p-5 shadow-sm sm:p-6">
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-500">Admin Workspace</p>
    <h1 class="mt-2 text-2xl font-semibold text-blue-950 sm:text-3xl">Platform Operations Overview</h1>
    <p class="mt-1 text-sm text-slate-600">
      Use the sidebar or module tiles to manage therapists, users, appointments, reporting, and platform controls.
    </p>
  </header>

  <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {#each modules as module (module.id)}
      <a
        href={module.route}
        class="group rounded-2xl border border-blue-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-700">
            <i class={`fa-solid ${module.icon}`}></i>
          </div>
          <div class="text-right">
            <p class="text-xl font-semibold text-blue-900">{module.metric}</p>
            <p class="text-xs text-slate-500">{module.metricLabel}</p>
          </div>
        </div>

        <h2 class="mt-4 text-lg font-semibold text-slate-900 group-hover:text-blue-700">{module.title}</h2>
        <p class="mt-1 text-sm text-slate-600">{module.description}</p>
      </a>
    {/each}
  </div>

  <article class="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">
    <h2 class="text-lg font-semibold text-blue-950">Backend-aware admin capabilities</h2>
    <ul class="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
      <li>Role governance via `is_staff` / `is_superuser` controls and inferred user type.</li>
      <li>Therapist profile lifecycle management linked to user records.</li>
      <li>Appointment pipeline operations (confirm, cancel, no-show handling, reschedule workflows).</li>
      <li>Operational analytics and audit visibility for compliance and quality control.</li>
    </ul>
  </article>
</section>
