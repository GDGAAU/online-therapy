import adapter from "@sveltejs/adapter-auto";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // vitePreprocess is still needed for <style> and <script lang="ts"> blocks
  preprocess: vitePreprocess(),

  compilerOptions: {
    // In Svelte 5, explicitly setting runes: true ensures all components 
    // use the new reactivity system and improves build performance.
    runes: true,
  },

  kit: {
    adapter: adapter(),
    alias: {
      "@": "./src/lib",
    },
  },
};

export default config;
