import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '../HomeView.vue'
import { useAuthStore, type Company, type Membership } from '@/stores/auth'
import { getDashboard } from '@/services/analytics'

vi.mock('@/services/analytics', () => ({
  getDashboard: vi.fn<typeof getDashboard>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture/nova', name: 'invoice-new', component: { template: '<div/>' } },
    { path: '/klijenti/novi', name: 'client-new', component: { template: '<div/>' } },
    { path: '/podesavanja', name: 'settings', component: { template: '<div/>' } },
    { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
  ],
})

function membership(companyOverrides: Partial<Company> = {}): Membership {
  return {
    role: 'owner',
    status: 'active',
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
      ...companyOverrides,
    },
  }
}

function mountHome() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const auth = useAuthStore()
  auth.user = {
    id: 1,
    email: 'marko@pausalac.rs',
    first_name: 'Marko',
    last_name: '',
    is_email_verified: true,
    memberships: [membership()],
  }
  return mount(HomeView, { global: { plugins: [pinia, router] } })
}

describe('HomeView (dashboard)', () => {
  beforeEach(() => {
    vi.mocked(getDashboard).mockReset()
  })

  it('shows the ok health status and an empty attention state', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'ok', reasons: [] },
      attention: [],
      revenue: { ytd: '0.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00' },
      onboarding: { completed: ['company', 'bank', 'client'], missing: ['sef', 'tax_document'], percentage: 60 },
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Sve je u redu')
    expect(wrapper.text()).toContain('Trenutno nema stavki')
  })

  it('shows the critical status and an overdue attention item', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'critical', reasons: ['1 faktura(e) kasni sa naplatom.'] },
      attention: [
        {
          type: 'overdue_invoices',
          message: '1 faktura(e) kasni sa ukupno 1.000,00 RSD potraživanja.',
          action: { route: 'invoices', query: { status: 'overdue' } },
        },
      ],
      revenue: { ytd: '1000.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 1, total: '1000.00', currency: 'RSD', overdue_count: 1, overdue_total: '1000.00' },
      onboarding: { completed: ['company', 'bank', 'client'], missing: ['sef', 'tax_document'], percentage: 60 },
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Potrebna akcija')
    expect(wrapper.text()).toContain('1 faktura(e) kasni')
  })

  it('shows the onboarding-completion bar only when incomplete', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'ok', reasons: [] },
      attention: [],
      revenue: { ytd: '0.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00' },
      onboarding: { completed: [], missing: [], percentage: 100 },
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Dovrši podešavanje')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(getDashboard).mockRejectedValue(new Error('boom'))
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno da učitamo pregled.')
  })
})
