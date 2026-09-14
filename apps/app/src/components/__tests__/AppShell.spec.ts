import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AppShell from '../AppShell.vue'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { listNotifications } from '@/services/notifications'

vi.mock('@/services/notifications', () => ({
  listNotifications: vi.fn<typeof listNotifications>(),
}))

function authenticatedUser() {
  return {
    id: 1,
    email: 'marko@pausalac.rs',
    first_name: '',
    last_name: '',
    is_email_verified: true,
    memberships: [
      {
        role: 'owner' as const,
        status: 'active' as const,
        company: {
          id: 1,
          name: 'Firma A',
          legal_name: '',
          pib: null,
          address: '',
          city: '',
          country: 'RS',
          activity_code: '',
          default_currency: 'RSD',
          bank_account: '',
          uses_sef: false,
          is_active: true,
          created_at: '',
          updated_at: '',
        },
      },
    ],
  }
}

describe('AppShell nav active state', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.mocked(listNotifications).mockReset()
    vi.mocked(listNotifications).mockResolvedValue({
      count: 0,
      next: null,
      previous: null,
      results: [],
    })
    const auth = useAuthStore()
    auth.status = 'authenticated'
    auth.user = authenticatedUser()
    await router.push({ name: 'invoices' })
    await router.isReady()
  })

  it('gives only the active link a background pill — not both colors on one element', async () => {
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const active = wrapper.findAll('a').find((a) => a.text() === 'Fakture')
    const inactive = wrapper.findAll('a').find((a) => a.text() === 'Klijenti')

    expect(active).toBeTruthy()
    expect(inactive).toBeTruthy()
    // The bug this guards against: RouterLink's active-class used to be
    // appended alongside the base class, leaving both text-primary and
    // text-text-secondary on the active element at once — an equal-
    // specificity collision that made the "active" color never actually
    // win the cascade. A single element must never carry both.
    expect(active!.classes()).toContain('bg-primary/10')
    expect(active!.classes()).toContain('text-primary')
    expect(active!.classes()).not.toContain('text-text-secondary')

    expect(inactive!.classes()).not.toContain('bg-primary/10')
    expect(inactive!.classes()).not.toContain('text-primary')
    expect(inactive!.classes()).toContain('text-text-secondary')
  })
})
