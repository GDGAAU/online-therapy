// tailwind.config.cjs
/** @type {import('tailwindcss').Config} */
module.exports = {
  // IMPORTANT: point 'content' at every place you use Tailwind classes
  content: [
    './src/**/*.{html,js,svelte,ts}',
    // include other folders if you have components outside src/
  ],

  // Dark mode strategy (class => you toggle a "dark" class on <html> or <body>)
  darkMode: 'class',

  theme: {
  extend: {
    colors: {
      brand: {
        DEFAULT: '#0ea5a4',
        50: '#ecfdfb',
        100: '#cffaf6',
      },
    },
    fontFamily: {
      sans: ['Inter', 'ui-sans-serif', 'system-ui'],
    },
    borderRadius: {
      lg: 'var(--radius)',
      md: 'calc(var(--radius) - 2px)',
      sm: 'calc(var(--radius) - 4px)',
    },
  },
  },

  plugins: [
    // add plugins here if you install them, e.g. require('@tailwindcss/forms')
  ],
};