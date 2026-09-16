import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '../HomeView.vue'
import { useAuthStore, type Company, type Membership } from '@/stores/auth'
import { getDashboard } from '@/services/analytics'
import type { LimitTrackerData, Limits } from '@/services/limits'

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
    { path: '/limiti', name: 'limits', component: { template: '<div/>' } },
    { path: '/obaveze', name: 'obligations', component: { template: '<div/>' } },
  ],
})

function limitTracker(overrides: Partial<LimitTrackerData> = {}): LimitTrackerData {
  return {
    identifier: 'pausal_turnover_limit',
    period: { type: 'calendar_year', start: '2026-01-01', end: '2026-12-31' },
    threshold: '6000000.00',
    current: '2840000.00',
    currency: 'RSD',
    percentage: 47,
    remaining: '3160000.00',
    warning_level: 'ok',
    projection: null,
    approval_status: 'unverified',
    ...overrides,
  }
}

function limitsFixture(): Limits {
  return {
    pausal_limit: limitTracker(),
    vat_threshold: limitTracker({
      identifier: 'vat_registration_threshold',
      period: { type: 'trailing_12_months', start: '2025-09-14', end: '2026-09-14' },
      threshold: '8000000.00',
      percentage: 12,
    }),
  }
}

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
    is_staff: false,
    language: 'sr',
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
      limits: limitsFixture(),
      next_obligation: null,
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
      limits: limitsFixture(),
      next_obligation: null,
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
      limits: limitsFixture(),
      next_obligation: null,
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Dovrši podešavanje')
  })

  it('shows both limits with a real progress bar each, not just bare percentages', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'ok', reasons: [] },
      attention: [],
      revenue: { ytd: '0.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00' },
      onboarding: { completed: ['company', 'bank', 'client'], missing: ['sef', 'tax_document'], percentage: 60 },
      limits: limitsFixture(),
      next_obligation: null,
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Limiti')
    expect(wrapper.text()).toContain('Paušalni limit')
    expect(wrapper.text()).toContain('PDV prag')
    expect(wrapper.text()).toContain('47%')
    expect(wrapper.text()).toContain('12%')
    expect(wrapper.findAll('[role="progressbar"]')).toHaveLength(2)
  })

  it('shows the next obligation card when one exists, flagging overdue', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'critical', reasons: ['Poreska obaveza kasni.'] },
      attention: [
        {
          type: 'tax_obligation_overdue',
          message: 'Poreska obaveza za 2026-01-01 kasni (45050.00 RSD).',
          action: { route: 'obligations' },
        },
      ],
      revenue: { ytd: '0.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00' },
      onboarding: { completed: ['company', 'bank', 'client'], missing: ['sef', 'tax_document'], percentage: 60 },
      limits: limitsFixture(),
      next_obligation: {
        period_start: '2026-01-01',
        due_date: '2026-02-16',
        total_amount: '45050.00',
        currency: 'RSD',
        status: 'overdue',
      },
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Sledeća obaveza')
    expect(wrapper.text()).toContain('45.050,00 RSD')
    expect(wrapper.text()).toContain('kasni')
  })

  it('shows a no-obligations message when next_obligation is null', async () => {
    vi.mocked(getDashboard).mockResolvedValue({
      business_health: { status: 'ok', reasons: [] },
      attention: [],
      revenue: { ytd: '0.00', currency: 'RSD', basis: 'invoiced' },
      outstanding: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00' },
      onboarding: { completed: ['company', 'bank', 'client'], missing: ['sef', 'tax_document'], percentage: 60 },
      limits: limitsFixture(),
      next_obligation: null,
    })
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Nema predstojećih obaveza.')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(getDashboard).mockRejectedValue(new Error('boom'))
    const wrapper = mountHome()
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno da učitamo pregled.')
  })
})
