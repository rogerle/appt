import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    
    // Coverage settings (Apple Design System: clean code coverage)
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{vue,js,ts}'],
      exclude: [
        'node_modules/',
        '.vite/',
        '**/main.js',
        '**/router/index.js'
      ]
    },
    
    // Clear DOM between tests for isolation (Apple principle of clarity)
    clearMocks: true,
    restoreMocks: true,
    
    // Test file pattern
    includeSource: ['src/**/*.{vue,js,ts}'],
    
    // Timeout per test (fast feedback loop)
    timeout: 5000
  }
})
