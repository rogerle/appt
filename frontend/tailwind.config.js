/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Soft, calming yoga-inspired palette (Apple HIG compliant)
        primary: {
          50: '#f8fafc',   // Very light gray-mint (backgrounds)
          100: '#f1f5f9',  // Light gray-mint
          200: '#e2e8f0',  // Borders/dividers
          300: '#cbd5e1',  // Secondary text
          400: '#94a3b8',  // Disabled states
          500: '#64748b',  // Muted elements
          600: '#475569',  // Body text
          700: '#334155',  // Headings
          800: '#1e293b',  // Strong emphasis
          900: '#0f172a',  // Primary CTA (dark)
        },
        
        accent: {
          green: '#10b981',     // Success/Available
          light: '#d1fae5',     // Light success background
          dark: '#047857'       // Dark success text
        },
        
        warning: {
          red: '#ef4444',       // Error/Cancelled
          light: '#fee2e2',     // Light error background
          dark: '#b91c1c'       // Dark error text
        }
      },
      
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif'
        ]
      },
      
      spacing: {
        '18': '4.5rem',     // Custom spacing for larger gaps
        '22': '5.5rem',
        '30': '7.5rem',
      },
      
      borderRadius: {
        'xl': '1rem',         // Larger rounded corners for cards
        '2xl': '1.5rem'       // Extra large for modals/dialogs
      }
    },
  },
  plugins: [],
}
