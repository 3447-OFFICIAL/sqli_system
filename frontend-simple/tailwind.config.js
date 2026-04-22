/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          black: "#020c1b",
          navy: "#0a192f",
          light: "#112240",
          accent: "#64ffda",
          red: "#ff3131",
          green: "#00ff9d",
          text: "#ccd6f6",
          dim: "#8892b0",
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
