import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/main.css'],
  modules: ['@nuxtjs/i18n'],
  app: {
    head: {
      // `<html lang>` is managed by @nuxtjs/i18n per active locale (its
      // head module reacts to the current route's locale) — no static
      // override here.
      titleTemplate: (title) => (title ? `${title} — Pausalac` : 'Pausalac'),
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  // Trilingual site (sr primary/default, ru and en optional — user
  // decision, this session, not in the original spec docs). `sr` sits at
  // the bare path with no prefix (primary language, and matches every
  // link built before this existed); `en`/`ru` get real, crawlable
  // `/en/...`/`/ru/...` prefixes rather than a client-side-only switch,
  // since this is a public, SSG-prerendered site where shareable/
  // indexable per-language URLs matter (unlike apps/app, an authenticated
  // SPA with no SEO surface, which stores the preference on the user
  // instead — see docs/decisions-log.md).
  i18n: {
    // Needed for the hreflang <link rel="alternate"> tags to be absolute
    // URLs — no real domain is confirmed yet (see docs/decisions-log.md),
    // so this stays env-var-driven with a safe localhost default, same
    // pattern as runtimeConfig.public.appUrl below. Override via
    // NUXT_PUBLIC_I18N_BASE_URL once a real domain exists.
    baseUrl: process.env.NUXT_PUBLIC_I18N_BASE_URL || 'http://localhost:3000',
    strategy: 'prefix_except_default',
    defaultLocale: 'sr',
    langDir: 'locales',
    locales: [
      { code: 'sr', language: 'sr-Latn', name: 'Srpski', file: 'sr.json' },
      { code: 'en', language: 'en-US', name: 'English', file: 'en.json' },
      { code: 'ru', language: 'ru-RU', name: 'Русский', file: 'ru.json' },
    ],
    // Explicitly `false`, not just omitted — @nuxtjs/i18n enables
    // Accept-Language-based redirects BY DEFAULT even with no
    // `detectBrowserLanguage` key present at all (found the hard way: it
    // silently 302'd an anonymous Playwright visitor, whose browser
    // locale is en-US, from `/` to `/en`, confirmed via a raw curl with
    // an Accept-Language header). Serbian is the primary/default language
    // regardless of the visitor's browser settings (master prompt §83) —
    // the switcher is the only way to change it, and the chosen locale
    // simply lives in the URL from then on.
    detectBrowserLanguage: false,
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
