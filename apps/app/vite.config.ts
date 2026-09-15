import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// The repo-root .env is the single source of truth for both the backend
// (apps/api reads it via django-environ) and this app — no separate
// apps/app/.env to keep in sync.
const envDir = fileURLToPath(new URL('../..', import.meta.url))
const env = loadEnv(process.env.NODE_ENV ?? 'development', envDir, '')

// https://vite.dev/config/
export default defineConfig({
  envDir,
  plugins: [
    vue(),
    // Off by default — its floating toggle button is fixed to the bottom
    // of the viewport and collides with the mobile bottom nav/FAB (Phase
    // 6d). Opt in with VITE_DEVTOOLS=true in .env when you actually want
    // the Components/Timeline inspector.
    ...(env.VITE_DEVTOOLS === 'true' ? [vueDevTools()] : []),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
