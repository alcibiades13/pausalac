import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

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
    // Master prompt §54's "Vue app -> responsive web -> PWA -> Capacitor"
    // pipeline, PWA stage (Phase 6f). `generateSW`'s default precache
    // scope is only the built JS/CSS/HTML/image assets emitted below —
    // deliberately no `runtimeCaching` entries are added for `/api/*`,
    // since caching live invoice/payment/tax data offline would be a
    // correctness risk for a financial app, not a feature. Disabled
    // during `pnpm dev` (`devOptions.enabled` defaults to false) so a
    // stale service worker never shadows local changes.
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'logo.svg', 'apple-touch-icon-180x180.png'],
      manifest: {
        name: 'Pausalac',
        short_name: 'Pausalac',
        description: 'Vođenje poslovanja za paušalne preduzetnike.',
        lang: 'sr',
        start_url: '/',
        display: 'standalone',
        theme_color: '#0a7067',
        background_color: '#f6f7fb',
        icons: [
          { src: 'pwa-64x64.png', sizes: '64x64', type: 'image/png' },
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          {
            src: 'maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
