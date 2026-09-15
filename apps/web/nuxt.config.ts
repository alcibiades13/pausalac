import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/main.css'],
  app: {
    head: {
      htmlAttrs: { lang: 'sr-Latn' },
      titleTemplate: (title) => (title ? `${title} — Pausalac` : 'Pausalac'),
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  runtimeConfig: {
    public: {
      // apps/app's real URL — CTAs ("Probaj besplatno"/"Prijavi se") link
      // there. Local dev default matches its Vite port; the real staging/
      // production domain topology is a deployment decision, not made
      // here (see docs/implementation-plan.md's "Hosting/deployment
      // target... out of scope" line) — override via NUXT_PUBLIC_APP_URL.
      appUrl: 'http://localhost:5173',
      // Same default apps/app's own api.ts falls back to.
      apiBase: 'http://localhost:8000/api',
    },
  },
})
