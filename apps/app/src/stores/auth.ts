import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { apiFetch } from '@/lib/api'

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
      status.value = 'authenticated'
    } catch {
      user.value = null
      status.value = 'guest'
    }
  }

  async function refreshMe() {
    user.value = await apiFetch<Me>('auth/me/')
  }

  async function register(payload: {
    email: string
    password: string
    first_name?: string
    last_name?: string
  }) {
    user.value = await apiFetch<Me>('auth/register/', { method: 'POST', body: payload })
    status.value = 'authenticated'
  }

  async function login(payload: { email: string; password: string }) {
    user.value = await apiFetch<Me>('auth/login/', { method: 'POST', body: payload })
    status.value = 'authenticated'
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
  }
})
