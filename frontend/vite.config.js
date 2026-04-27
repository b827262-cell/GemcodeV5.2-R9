import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 3001,
    strictPort: true,
    allowedHosts: true,
    proxy: {
      // 🌟 修正：正確攔截 /api 並轉發到 backend 容器，同時移除 /api 前綴
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
    // 🌟 修正：移除硬編碼的 clientPort: 443，避免 localhost 下出現連線拒絕
    hmr: true,
    watch: {
      usePolling: true,
      interval: 100,
    },
  },
});
