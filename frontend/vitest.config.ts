import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // The real entry throws outside React Server Components; tests run backend code directly.
      'server-only': path.resolve(__dirname, './node_modules/server-only/empty.js'),
    },
  },
})
