import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminShell from '../AdminShell.vue'
import router from '@/router'
import { i18n } from '@/i18n'
import { useAuthStore } from '@/stores/auth'

function staffUser() {
  return {
    id: 1,
    email: 'admin@pausalac.rs',
    first_name: '',
    last_name: '',
    is_email_verified: true,
    is_staff: true,
    language: 'sr',
    memberships: [],
  }
}

describe('AdminShell sidebar (tablet/desktop nav)', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.status = 'authenticated'
    auth.user = staffUser()
    await router.push({ name: 'admin-companies' })
    await router.isReady()
  })

  it('renders the sidebar hidden below sm and visible from sm up', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('hidden')
    expect(aside.classes()).toContain('sm:flex')
  })

  it('renders all 11 admin nav links inside the sidebar', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    const labels = [
      'Korisnici',
      'Kompanije',
      'Pretplate',
      'Planovi',
      'Fakture',
      'Dokumenti',
      'Poreske obaveze',
      'Regulatorna pravila',
      'Obaveštenja',
      'Audit log',
      'Integracije',
    ]
    for (const label of labels) {
      expect(aside.text(), `missing sidebar link: ${label}`).toContain(label)
    }
  })

  it('gives only the active link a background pill', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    const active = aside.findAll('a').find((a) => a.text() === 'Kompanije')!
    const inactive = aside.findAll('a').find((a) => a.text() === 'Korisnici')!

    expect(active.classes()).toContain('bg-primary/10')
    expect(active.classes()).toContain('text-primary')
    expect(inactive.classes()).not.toContain('bg-primary/10')
    expect(inactive.classes()).toContain('text-text-secondary')
  })

  it('labels the sidebar nav landmark "Admin navigacija"', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    expect(wrapper.get('aside nav').attributes('aria-label')).toBe('Admin navigacija')
  })

  it('shows the current user email and an exit action in the sidebar footer', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const aside = wrapper.get('aside')
    expect(aside.text()).toContain('admin@pausalac.rs')
    expect(aside.text()).toContain('Nazad u aplikaciju')
  })

  it('exits to the main app when "Nazad u aplikaciju" is clicked', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const exitButton = wrapper.get('aside').findAll('button').find((b) => b.text() === 'Nazad u aplikaciju')!
    await exitButton.trigger('click')

    await vi.waitFor(() => {
      expect(router.currentRoute.value.name).toBe('home')
    })
  })

  it('keeps a mobile-only header with its own nav row for viewports below sm', async () => {
    const wrapper = mount(AdminShell, { global: { plugins: [pinia, router, i18n] } })
    await flushPromises()

    const header = wrapper.get('header')
    expect(header.classes()).toContain('sm:hidden')
    expect(header.text()).toContain('Kompanije')
  })
})
