/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        navy: "#0F2847",
        teal2: "#009688",
        ink: "#0b1020",
        paper: "#f6f8fb"
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "Arial", "sans-serif"]
      }
    }
  },
  plugins: []
};
