/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Razorpay Brand Palette
        rzp: {
          blue:       '#0C83FD',
          hover:      '#0273E8',
          dark:       '#02042B',
          navy:       '#081028',
          card:       'rgba(11,21,46,0.75)',
          cardBorder: 'rgba(12,131,253,0.22)',
          emerald:    '#00BA74',
          cyan:       '#00BAF2',
          purple:     '#6851FF',
          amber:      '#FF9900',
        },
        // Glass system tokens
        glass: {
          bg:     'rgba(12,131,253,0.06)',
          border: 'rgba(12,131,253,0.18)',
          strong: 'rgba(11,21,46,0.85)',
          card:   'rgba(11,21,46,0.75)',
          dark:   'rgba(2,4,43,0.92)',
        },
        neon: {
          blue:    '#0C83FD',
          cyan:    '#00BAF2',
          emerald: '#00BA74',
          purple:  '#6851FF',
          rose:    '#fb7185',
          amber:   '#FF9900',
          indigo:  '#0C83FD',
        },
        // Backwards-compatible aliases so existing pages don't break
        fintech: {
          dark:       '#02042B',
          card:       'rgba(11,21,46,0.75)',
          cardBorder: 'rgba(12,131,253,0.20)',
          accent:     '#0C83FD',
          accentHover:'#0273E8',
          emerald:    '#00BA74',
          rose:       '#fb7185',
          amber:      '#FF9900',
          purple:     '#6851FF',
        },
      },
      boxShadow: {
        'neon-blue':    '0 0 20px rgba(56,189,248,0.35),  0 0 60px rgba(56,189,248,0.12)',
        'neon-cyan':    '0 0 20px rgba(34,211,238,0.35),  0 0 60px rgba(34,211,238,0.12)',
        'neon-emerald': '0 0 20px rgba(52,211,153,0.35),  0 0 60px rgba(52,211,153,0.12)',
        'neon-purple':  '0 0 20px rgba(167,139,250,0.35), 0 0 60px rgba(167,139,250,0.12)',
        'neon-rose':    '0 0 20px rgba(251,113,133,0.35), 0 0 60px rgba(251,113,133,0.12)',
        'neon-amber':   '0 0 20px rgba(251,191,36,0.35),  0 0 60px rgba(251,191,36,0.12)',
        'glass':        '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08)',
        'glass-lg':     '0 16px 64px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.10)',
        'glass-sm':     '0 4px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06)',
      },
      animation: {
        'aurora':      'aurora 16s ease infinite alternate',
        'float':       'float 6s ease-in-out infinite',
        'glow-pulse':  'glowPulse 2.5s ease-in-out infinite',
        'shimmer':     'shimmer 2s linear infinite',
      },
      keyframes: {
        aurora: {
          '0%':   { backgroundPosition: '0% 50%' },
          '50%':  { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
        glowPulse: {
          '0%, 100%': { opacity: '0.8' },
          '50%':      { opacity: '1'   },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0'  },
        },
      },
    },
  },
  plugins: [],
}

