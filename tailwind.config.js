/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        background: '#F8FAFC',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
