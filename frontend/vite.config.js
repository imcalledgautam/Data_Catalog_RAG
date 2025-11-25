import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://data-catalog-rag-291677621486.europe-west1.run.app',
        changeOrigin: true,
      },
    },
  },
})
