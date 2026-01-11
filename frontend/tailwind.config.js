/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // Add this line
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Define theme-aware colors
        brand: {
          bg: 'var(--bg-color)',
          card: 'var(--card-color)',
        }
      }
    },
  },
  plugins: [],
}