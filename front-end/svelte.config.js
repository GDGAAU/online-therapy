import adapter from "@sveltejs/adapter-auto";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    alias: {
      // $lib is automatically aliased by SvelteKit
      // Add additional aliases here if needed
      "@/*": "./src/lib/*",
    },
  },
};

export default config;
