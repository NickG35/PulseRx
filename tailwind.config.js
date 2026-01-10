/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./patients/templates/**/*.html",
    "./pharmacy/templates/**/*.html",
    "./accounts/templates/**/*.html",
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        // Primary Brand Colors (Heart/Pulse Theme)
        'pulse-primary': {
          DEFAULT: '#0066CC',
          dark: '#0052A3',
          light: '#3384D6',
        },
        'pulse-red': {
          DEFAULT: '#B91C1C', // Darker red for badges/accents
          dark: '#991B1B',
          light: '#DC2626',
        },
        'pulse-cream': {
          DEFAULT: '#FFF8F0', // Warm cream background
          dark: '#FFF0E0',
        },

        // Semantic Colors
        'pulse-success': {
          DEFAULT: '#10B981',
          dark: '#059669',
          light: '#34D399',
        },
        'pulse-warning': {
          DEFAULT: '#F59E0B',
          dark: '#D97706',
          light: '#FBBF24',
        },
        'pulse-danger': {
          DEFAULT: '#EF4444',
          dark: '#DC2626',
          light: '#F87171',
        },

        // Feature Accent Colors
        'pulse-purple': {
          DEFAULT: '#8B5CF6',
          dark: '#7C3AED',
          light: '#A78BFA',
        },
        'pulse-teal': {
          DEFAULT: '#14B8A6',
          dark: '#0D9488',
          light: '#2DD4BF',
        },
        'pulse-sky': {
          DEFAULT: '#0EA5E9',
          dark: '#0284C7',
          light: '#38BDF8',
        },

        // Neutral Colors
        'pulse-gray': {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
    },
  },
  plugins: [require('daisyui').default || require('daisyui')],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "oklch(45% 0.24 277)",
          "secondary": "oklch(65% 0.241 354)",
          "accent": "oklch(77% 0.152 181)",
          "neutral": "oklch(14% 0.005 285)",
          "base-100": "oklch(100% 0 0)",
          "info": "oklch(74% 0.16 232)",
          "success": "oklch(76% 0.177 163)",
          "warning": "oklch(82% 0.189 84)",
          "error": "oklch(49% 0.19 27)", // Pulse-red #B91C1C in oklch
          "error-content": "oklch(100% 0 0)", // White text on red
        },
      },
    ],
    base: true, // Apply base DaisyUI styles
    styled: true, // Include DaisyUI component styles
    utils: true, // Include DaisyUI utility classes
  },
}
