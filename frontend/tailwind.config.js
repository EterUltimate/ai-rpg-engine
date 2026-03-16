/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 游戏主题色
        'game-primary': '#6366f1',
        'game-secondary': '#8b5cf6',
        'game-accent': '#f59e0b',
        'game-dark': '#1e1b4b',
        'game-light': '#f3f4f6',
      },
      fontFamily: {
        'game': ['Press Start 2P', 'Courier New', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
    },
  },
  plugins: [],
}
