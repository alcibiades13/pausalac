import { createI18n } from 'vue-i18n'
import sr from './locales/sr'
import en from './locales/en'
import ru from './locales/ru'

/**
 * i18n-b (docs/decisions-log.md): sr is primary/default (master prompt
 * §83); en/ru are user-selectable, persisted via `User.language`
 * (apps/api/apps/accounts — added in i18n-a) once logged in, and via
 * localStorage before that (register/login/forgot-password screens have
 * no authenticated user yet to read a preference from). See
 * stores/auth.ts's `setLanguage` for the write path — this module only
 * owns the i18n instance and the read-before-login fallback.
 *
 * `legacy: false` (Composition API mode) — every consuming component
 * uses `useI18n()`/`$t()`, matching the same convention apps/web's
 * @nuxtjs/i18n already established this session. No `tm()`/`rt()` here:
 * that was a real bug apps/web hit (the compiled message AST leaking as
 * literal page text) — this app avoids the whole class of bug by never
 * pulling structured list content through `tm()`; anywhere a view loops
 * over translatable items, it loops over plain key strings and calls
 * `t()` per key instead.
 */
export const SUPPORTED_LANGUAGES = ['sr', 'en', 'ru'] as const
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

const STORAGE_KEY = 'pausalac_language'

function isSupportedLanguage(value: string | null): value is SupportedLanguage {
  return value !== null && (SUPPORTED_LANGUAGES as readonly string[]).includes(value)
}

function detectInitialLocale(): SupportedLanguage {
  const stored = localStorage.getItem(STORAGE_KEY)
  return isSupportedLanguage(stored) ? stored : 'sr'
}

export const i18n = createI18n({
  legacy: false,
  locale: detectInitialLocale(),
  fallbackLocale: 'sr',
  messages: { sr, en, ru },
})

/**
 * Switches the active UI language immediately (no page reload) and
 * remembers the choice in localStorage — the pre-login fallback, and
 * also what a still-logged-in tab falls back to if a `PATCH /auth/me/`
 * call (stores/auth.ts::setLanguage) fails. `document.documentElement
 * .lang` is set directly (no framework-level `<html lang>` binding
 * exists in this SPA, unlike apps/web's Nuxt `useLocaleHead()`).
 */
export function applyLocale(lang: SupportedLanguage) {
  i18n.global.locale.value = lang
  localStorage.setItem(STORAGE_KEY, lang)
  document.documentElement.lang = lang
}
