/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "gov-blue": "#003366",
        "alert-red": "#d32f2f",
      }
    },
  },
  plugins: [],
}