import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '127.0.0.1',
    strictPort: false,  // Essayer un autre port si occupé
    open: true  // Ouvrir le navigateur automatiquement
  }
})