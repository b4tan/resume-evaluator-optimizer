/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", 
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        darkBlue: "#1E3A8A", 
        offWhite: "#F8F9FA", 
      },
      container: {
        center: true,
        padding: "2rem",
      },
    },
  },
  plugins: [],
};
