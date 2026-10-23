import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const appRoot = fileURLToPath(new URL('./app/', import.meta.url));
const output = fileURLToPath(new URL('./app/dist/', import.meta.url));

export default defineConfig({
  root: appRoot,
  plugins: [react()],
  base: '/',
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  build: {
    outDir: output,
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/@mantine/') || id.includes('node_modules/@floating-ui/')) return 'ui';
          if (id.includes('node_modules/@tabler/icons-react/')) return 'icons';
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/') || id.includes('node_modules/scheduler/')) return 'react';
          return undefined;
        },
      },
    },
  },
});
