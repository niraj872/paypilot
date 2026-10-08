/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#07111f',
        panel: '#0d1a2b',
        line: '#203149',
        mint: '#5eead4',
        sky: '#60a5fa',
        amber: '#fbbf24'
      },
      boxShadow: {
        glow: '0 0 50px rgba(96,165,250,0.12)'
      }
    }
  },
  plugins: []
};
