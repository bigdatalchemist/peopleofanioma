/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "../backend/templates/**/*.html",
    "../backend/apps/**/templates/**/*.html",
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
        poppins: ['Poppins', 'sans-serif'],
        playfair: ['"Playfair Display"', 'serif'],
        raleway: ['Raleway', 'sans-serif'],
        ubuntu: ['Ubuntu', 'sans-serif'],
        merriweather: ['Merriweather', 'serif'],
        lora: ['Lora', 'serif'],
        cabin: ['Cabin', 'sans-serif'],
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
  variants: {
    extend: {
      backgroundColor: ['dark'],
      textColor: ['dark'],
      borderColor: ['dark'],
      ringColor: ['dark'],
      placeholderColor: ['dark'],
    },
  },
  plugins: [],
}
