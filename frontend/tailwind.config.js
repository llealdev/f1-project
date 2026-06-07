/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Titillium Web"', '"Inter"', 'system-ui', 'sans-serif'],
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      colors: {
        f1: {
          red: '#E10600',
          dark: '#15151E',
          carbon: '#1F1F27',
          gray: '#38383F',
          light: '#F7F7F7',
        },
      },
      backgroundImage: {
        'f1-gradient': 'linear-gradient(135deg, #E10600 0%, #7A0000 100%)',
        'carbon': 'radial-gradient(circle at 30% 0%, rgba(225,6,0,0.15), transparent 40%), radial-gradient(circle at 80% 100%, rgba(225,6,0,0.1), transparent 40%), linear-gradient(180deg, #15151E 0%, #1F1F27 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
