<script>
  import '../app.css';
  import Navbar from '$lib/components/layout/Navbar.svelte';
  import Footer from '$lib/components/layout/Footer.svelte';
</script>

<Navbar />
<main>
  <slot />  <!-- Your page content (home, login, etc.) will appear here -->
</main>
<Footer />
