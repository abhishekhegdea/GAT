/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          deepBlue: '#0B1C2D',
          indigo: '#1F3C88',
          cyan: '#00E5FF',
          softPurple: '#8A79FF',
          neonGreen: '#39FF14'
        },
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        }
      },
      boxShadow: {
        soft: '0 8px 24px rgba(0,0,0,0.12)',
        glass: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 12px 32px rgba(0,0,0,0.18)'
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.25rem'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
