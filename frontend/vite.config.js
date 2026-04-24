import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: true,
    port: 3001,
    strictPort: true,

    allowedHosts: true,

    watch: {
      usePolling: true
    },

    hmr: true,

    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
