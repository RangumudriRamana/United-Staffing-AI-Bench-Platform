import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';
import type { IncomingMessage } from 'node:http';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/consultants': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        bypass: (req: IncomingMessage) => {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/requirements': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        bypass: (req: IncomingMessage) => {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/submissions': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        bypass: (req: IncomingMessage) => {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html';
          }
        },
      },
      '/auth': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
});