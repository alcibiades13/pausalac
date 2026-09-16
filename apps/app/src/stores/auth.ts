import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { apiFetch } from '@/lib/api'
import { applyLocale, type SupportedLanguage } from '@/i18n'

export interface Company {
  id: number
  name: string
  legal_name: string
  pib: string | null
  address: string
  city: string
  country: string
  activity_code: string
  default_currency: string
  bank_account: string
  uses_sef: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Membership {
  company: Company
  role: 'owner' | 'accountant' | 'accountant_admin'
  status: 'active' | 'invited' | 'revoked'
}

export interface Me {
  id: number
  email: string
  first_name: string
  last_name: string
  is_email_verified: boolean
  /** UI-visibility signal only (master prompt §67, Phase 6b) — whether to
   * show the Admin entry point at all. The real gate is always the
   * backend's own IsAdminUser/IsSuperUser checks. */
  is_staff: boolean
  language: SupportedLanguage
  memberships: Membership[]
}

type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'guest'

export const useAuthStore = defineStore('auth', () => {
  const status = ref<AuthStatus>('idle')
  const user = ref<Me | null>(null)

  const isAuthenticated = computed(() => status.value === 'authenticated')

  async function primeCsrf() {
    await apiFetch('auth/csrf/')
  }

  /** Call once on app boot (see router/index.ts) — restores session state after a page refresh. */
  async function bootstrap() {
    if (status.value !== 'idle') return
    status.value = 'loading'
    try {
      await primeCsrf()
      user.value = await apiFetch<Me>('auth/me/')
      applyLocale(user.value.language)
      status.value = 'authenticated'
    } catch {
      user.value = null
      status.value = 'guest'
    }
  }

  async function refreshMe() {
    user.value = await apiFetch<Me>('auth/me/')
    applyLocale(user.value.language)
  }

  async function register(payload: {
    email: string
    password: string
    first_name?: string
    last_name?: string
  }) {
    user.value = await apiFetch<Me>('auth/register/', { method: 'POST', body: payload })
    applyLocale(user.value.language)
    status.value = 'authenticated'
  }

  async function login(payload: { email: string; password: string }) {
    user.value = await apiFetch<Me>('auth/login/', { method: 'POST', body: payload })
    applyLocale(user.value.language)
    status.value = 'authenticated'
  }

  /**
   * Persists the chosen language to the backend (so it follows the user
   * across devices/sessions) and switches the UI immediately rather than
   * waiting on the round-trip — `applyLocale` first, `PATCH` after, same
   * optimistic-update shape as everywhere else this store mutates local
   * state ahead of a request that rarely fails. If the request does fail,
   * the language still changed for this tab (localStorage-backed) —
   * silently swallowing the error here is deliberate, not an oversight:
   * a failed preference save isn't worth interrupting the user over, and
   * `user.value.language` gets reconciled on the next `refreshMe()`.
   */
  async function setLanguage(language: SupportedLanguage) {
    applyLocale(language)
    if (user.value) user.value.language = language
    try {
      await apiFetch<Me>('auth/me/', { method: 'PATCH', body: { language } })
    } catch {
      // see doc comment above
    }
  }

  async function resendVerificationEmail() {
    await apiFetch('auth/resend-verification/', { method: 'POST' })
  }

  async function logout() {
    try {
      await apiFetch('auth/logout/', { method: 'POST' })
    } finally {
      user.value = null
      status.value = 'guest'
    }
  }

  return {
    status,
    user,
    isAuthenticated,
    bootstrap,
    refreshMe,
    register,
    login,
    logout,
    resendVerificationEmail,
    setLanguage,
  }
})
