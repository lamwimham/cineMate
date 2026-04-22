/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 背景层级
        'bg-darkest': '#050508',
        'bg-dark': '#0a0a0f',
        'bg-base': '#13131f',
        'bg-elevated': '#1a1a2e',
        'bg-hover': '#252540',
        'bg-active': '#2d2d4d',
        // 品牌色
        'brand': '#6366f1',
        'brand-dim': '#4f46e5',
        // 状态色
        'success': '#22c55e',
        'success-dim': '#16a34a',
        'warning': '#f59e0b',
        'warning-dim': '#d97706',
        'error': '#ef4444',
        'error-dim': '#dc2626',
        'info': '#3b82f6',
        'info-dim': '#2563eb',
        // 文本色
        'text-primary': '#f1f5f9',
        'text-secondary': '#94a3b8',
        'text-tertiary': '#64748b',
        'text-muted': '#475569',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'monospace'],
      },
      fontSize: {
        'xs': ['11px', { lineHeight: '1.2', fontWeight: '500' }],
        'sm': ['13px', { lineHeight: '1.5', fontWeight: '400' }],
        'sm-b': ['13px', { lineHeight: '1.5', fontWeight: '600' }],
        'base': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'base-b': ['14px', { lineHeight: '1.5', fontWeight: '600' }],
        'lg': ['16px', { lineHeight: '1.4', fontWeight: '600' }],
        'xl': ['20px', { lineHeight: '1.3', fontWeight: '700' }],
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
      },
      borderRadius: {
        'sm': '6px',
        'DEFAULT': '8px',
        'md': '10px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'md': '0 4px 12px rgba(0, 0, 0, 0.4)',
        'lg': '0 8px 24px rgba(0, 0, 0, 0.5)',
        'glow-brand': '0 0 20px rgba(99, 102, 241, 0.15)',
        'glow-success': '0 0 20px rgba(34, 197, 94, 0.15)',
        'glow-warning': '0 0 20px rgba(245, 158, 11, 0.15)',
        'glow-error': '0 0 20px rgba(239, 68, 68, 0.15)',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shake': 'shake 500ms ease-in-out',
        'progress-flow': 'progressFlow 1s linear infinite',
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-up': 'slideUp 300ms ease-out',
        'scale-pop': 'scalePop 400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
        'check-draw': 'checkDraw 400ms ease-out forwards',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 8px rgba(245, 158, 11, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(245, 158, 11, 0.6)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '20%': { transform: 'translateX(-4px)' },
          '40%': { transform: 'translateX(4px)' },
          '60%': { transform: 'translateX(-2px)' },
          '80%': { transform: 'translateX(2px)' },
        },
        progressFlow: {
          '0%': { backgroundPosition: '0% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scalePop: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        checkDraw: {
          '0%': { strokeDashoffset: '24' },
          '100%': { strokeDashoffset: '0' },
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}
