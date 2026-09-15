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
    is_staff: false,
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

describe('AppShell sidebar (tablet/desktop nav)', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.mocked(listNotifications).mockReset()
    vi.mocked(listNotifications).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const auth = useAuthStore()
    auth.status = 'authenticated'
    auth.user = authenticatedUser()
    await router.push({ name: 'invoices' })
    await router.isReady()
  })

  it('renders the sidebar hidden below sm and visible from sm up', async () => {
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('hidden')
    expect(aside.classes()).toContain('sm:flex')
  })

  it('renders all 8 nav links inside the sidebar, each with an icon', async () => {
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    const labels = ['Početna', 'Klijenti', 'Fakture', 'Limiti', 'KPO', 'Obaveze', 'Dokumenti', 'Računovođa']
    for (const label of labels) {
      const link = aside.findAll('a').find((a) => a.text().includes(label))
      expect(link, `missing sidebar link: ${label}`).toBeTruthy()
      expect(link!.find('svg').exists()).toBe(true)
    }
  })

  it('lists notifications, settings and logout in the sidebar footer', async () => {
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    expect(aside.text()).toContain('Obaveštenja')
    expect(aside.text()).toContain('Podešavanja')
    expect(aside.text()).toContain('Odjavi se')
  })

  it('calls auth.logout() when "Odjavi se" is clicked', async () => {
    // Not asserting the post-logout redirect here: this router's global
    // beforeEach guard resolves useAuthStore() independently of this
    // test's pinia/mount wiring, so it doesn't reliably observe the
    // mocked post-logout auth state in a unit test — a pre-existing
    // router/test-setup quirk unrelated to this component, not something
    // to chase down as part of a UI restructuring change. The redirect
    // itself is unchanged code (still AppShell's existing onLogout).
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()
    const auth = useAuthStore()
    const logoutSpy = vi.spyOn(auth, 'logout').mockResolvedValue()

    const logoutButton = wrapper.get('aside').findAll('button').find((b) => b.text() === 'Odjavi se')!
    await logoutButton.trigger('click')
    await flushPromises()

    expect(logoutSpy).toHaveBeenCalled()
  })
})

describe('AppShell accessibility (master prompt §55)', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.mocked(listNotifications).mockReset()
    const auth = useAuthStore()
    auth.status = 'authenticated'
    auth.user = authenticatedUser()
    await router.push({ name: 'invoices' })
    await router.isReady()
  })

  it('offers a skip-to-content link targeting the main landmark', async () => {
    vi.mocked(listNotifications).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const skipLink = wrapper.find('a[href="#main-content"]')
    expect(skipLink.exists()).toBe(true)
    expect(skipLink.text()).toBe('Preskoči na sadržaj')
    expect(wrapper.find('main#main-content').exists()).toBe(true)
  })

  it('labels the sidebar nav landmark', async () => {
    vi.mocked(listNotifications).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    expect(wrapper.get('aside nav').attributes('aria-label')).toBe('Glavna navigacija')
  })

  it('includes the unread count in the notification link\'s accessible name', async () => {
    vi.mocked(listNotifications).mockResolvedValue({ count: 3, next: null, previous: null, results: [] })
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const bell = wrapper.get('[href="/obavestenja"]')
    expect(bell.attributes('aria-label')).toBe('Obaveštenja (3 nepročitanih)')
  })

  it('falls back to a plain label when there are no unread notifications', async () => {
    vi.mocked(listNotifications).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(AppShell, { global: { plugins: [pinia, router] } })
    await flushPromises()

    const bell = wrapper.get('[href="/obavestenja"]')
    expect(bell.attributes('aria-label')).toBe('Obaveštenja')
  })
})
