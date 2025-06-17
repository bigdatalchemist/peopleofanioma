/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "../backend/templates/**/*.html",
    "../backend/**/*.py",
    "../backend/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        aniomaBlue: '#1e40af',
        aniomaAmber: '#d97706',
      },
      fontFamily: {
        anioma: ['"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 1.2s ease-out forwards',
      },
    },
  },
  plugins: [],
}
