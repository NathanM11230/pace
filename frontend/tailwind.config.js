export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        blue: { DEFAULT: '#0066FF', 600: '#0052CC', 400: '#3385FF' },
        navy: { DEFAULT: '#1A1F36', light: '#252B45' },
        green: { DEFAULT: '#00D9A3', dark: '#00B386' },
        orange: '#FF6B35',
        gray: { light: '#F5F7FA', mid: '#E8ECF0', dark: '#6B7280' }
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }
    }
  }
}
