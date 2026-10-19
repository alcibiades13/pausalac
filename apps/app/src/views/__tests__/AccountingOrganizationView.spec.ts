import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import AccountingOrganizationView from '../AccountingOrganizationView.vue'
import {
  listOrganizations,
  createOrganization,
  listOrgStaff,
  addOrgStaff,
  removeOrgStaff,
  listOrgConnections,
  createOrgConnection,
  getClientPortfolio,
  type AccountingOrganization,
  type OrgStaffMembership,
  type OrganizationConnection,
  type ClientPortfolioRow,
} from '@/services/accounting'
import { useCompanyStore } from '@/stores/company'
import { i18n } from '@/i18n'

vi.mock('@/services/accounting', () => ({
  listOrganizations: vi.fn<typeof listOrganizations>(),
  createOrganization: vi.fn<typeof createOrganization>(),
  listOrgStaff: vi.fn<typeof listOrgStaff>(),
  addOrgStaff: vi.fn<typeof addOrgStaff>(),
  removeOrgStaff: vi.fn<typeof removeOrgStaff>(),
  listOrgConnections: vi.fn<typeof listOrgConnections>(),
  createOrgConnection: vi.fn<typeof createOrgConnection>(),
  getClientPortfolio: vi.fn<typeof getClientPortfolio>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/pocetna', name: 'home', component: { template: '<div/>' } },
  ],
})

function org(overrides: Partial<AccountingOrganization> = {}): AccountingOrganization {
  return {
    id: 1,
    name: 'Agencija Prime',
    contact_email: 'info@agencija.rs',
    pib: null,
    created_at: '2026-09-14T00:00:00Z',
    my_role: 'admin',
    ...overrides,
  }
}

function staffMember(overrides: Partial<OrgStaffMembership> = {}): OrgStaffMembership {
  return {
    id: 1,
    user: 1,
    user_email: 'staff@agencija.rs',
    organization: 1,
    role: 'staff',
    status: 'active',
    created_at: '2026-09-14T00:00:00Z',
    ...overrides,
  }
}

function connection(overrides: Partial<OrganizationConnection> = {}): OrganizationConnection {
  return {
    id: 1,
    company: 1,
    company_name: 'Firma A',
    company_pib: '123456789',
    granted_role: 'accountant',
    status: 'pending',
    created_at: '2026-09-14T00:00:00Z',
    accepted_at: null,
    revoked_at: null,
    ...overrides,
  }
}

function portfolioRow(overrides: Partial<ClientPortfolioRow> = {}): ClientPortfolioRow {
  return {
    company_id: 10,
    company_name: 'Firma Aktivna',
    company_pib: '999999999',
    granted_role: 'accountant',
    status: 'ok',
    revenue_ytd: '1000000.00',
    currency: 'RSD',
    pausal_limit: { percentage: 17, warning_level: 'ok' },
    vat_threshold: { percentage: 13, warning_level: 'ok' },
    next_obligation_due: null,
    next_obligation_overdue: false,
    overdue_invoice_count: 0,
    missing_document_count: 0,
    integration_errors: null,
    ...overrides,
  }
}

const EMPTY_PORTFOLIO_PAGE = {
  count: 0,
  next: null,
  previous: null,
  results: [] as ClientPortfolioRow[],
  summary: { total: 0, ok: 0, attention: 0, critical: 0 },
}

function mountView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(AccountingOrganizationView, { global: { plugins: [pinia, router, i18n] } })
}

describe('AccountingOrganizationView', () => {
  beforeEach(async () => {
    vi.mocked(listOrganizations).mockReset()
    vi.mocked(createOrganization).mockReset()
    vi.mocked(listOrgStaff).mockReset()
    vi.mocked(addOrgStaff).mockReset()
    vi.mocked(removeOrgStaff).mockReset()
    vi.mocked(listOrgConnections).mockReset()
    vi.mocked(createOrgConnection).mockReset()
    vi.mocked(getClientPortfolio).mockReset()
    vi.mocked(getClientPortfolio).mockResolvedValue(EMPTY_PORTFOLIO_PAGE)
    await router.push('/')
    await router.isReady()
  })

  it('shows the create-organization form when the user has none', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Osnuj agenciju')
  })

  it('creates an organization and switches to the org view', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(createOrganization).mockResolvedValue(org())

    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('input[required]').setValue('Agencija Prime')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createOrganization).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Agencija Prime')
  })

  it('loads staff and connections for an existing organization', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [org()],
    })
    vi.mocked(listOrgStaff).mockResolvedValue([staffMember()])
    vi.mocked(listOrgConnections).mockResolvedValue([connection()])

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.text()).toContain('staff@agencija.rs')
    expect(wrapper.text()).toContain('Firma A')
  })

  it('adds staff and reloads the staff list, as an admin', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [org({ my_role: 'admin' })],
    })
    vi.mocked(listOrgStaff).mockResolvedValue([])
    vi.mocked(listOrgConnections).mockResolvedValue([])
    vi.mocked(addOrgStaff).mockResolvedValue(staffMember())

    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('input[type="email"]').setValue('staff@agencija.rs')
    const forms = wrapper.findAll('form')
    await forms[0]!.trigger('submit.prevent')
    await flushPromises()

    expect(addOrgStaff).toHaveBeenCalledWith(1, { email: 'staff@agencija.rs', role: 'staff' })
    expect(listOrgStaff).toHaveBeenCalledTimes(2)
  })

  it('does not show the invite-staff form for a non-admin staff member', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [org({ my_role: 'staff' })],
    })
    vi.mocked(listOrgStaff).mockResolvedValue([staffMember()])
    vi.mocked(listOrgConnections).mockResolvedValue([])

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('input[type="email"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('Ukloni')
  })

  it('invites a client by PIB and reloads connections', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [org()],
    })
    vi.mocked(listOrgStaff).mockResolvedValue([])
    vi.mocked(listOrgConnections).mockResolvedValue([])
    vi.mocked(createOrgConnection).mockResolvedValue(connection())

    const wrapper = mountView()
    await flushPromises()

    const forms = wrapper.findAll('form')
    const clientForm = forms[forms.length - 1]!
    await clientForm.find('input').setValue('123456789')
    await clientForm.trigger('submit.prevent')
    await flushPromises()

    expect(createOrgConnection).toHaveBeenCalledWith(1, {
      company_pib: '123456789',
      granted_role: 'accountant',
    })
    expect(listOrgConnections).toHaveBeenCalledTimes(2)
  })

  describe('client portfolio', () => {
    beforeEach(() => {
      vi.mocked(listOrganizations).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [org()],
      })
      vi.mocked(listOrgStaff).mockResolvedValue([])
      vi.mocked(listOrgConnections).mockResolvedValue([connection({ status: 'pending' })])
    })

    it('renders portfolio rows with status/revenue/limit badges and the summary counts', async () => {
      vi.mocked(getClientPortfolio).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [portfolioRow({ status: 'critical', overdue_invoice_count: 2 })],
        summary: { total: 1, ok: 0, attention: 0, critical: 1 },
      })

      const wrapper = mountView()
      await flushPromises()

      expect(wrapper.text()).toContain('Firma Aktivna')
      expect(wrapper.text()).toContain('Kritično')
      expect(wrapper.text()).toContain('Paušal 17%')
      expect(wrapper.text()).toContain('PDV 13%')
      // Pending connection still shows in its own list, separate from the
      // active-only portfolio table.
      expect(wrapper.text()).toContain('Na čekanju')
      expect(wrapper.text()).toContain('Firma A')
    })

    it('shows an empty state when there are no active clients', async () => {
      const wrapper = mountView()
      await flushPromises()
      expect(wrapper.text()).toContain('Nema aktivnih klijenata.')
    })

    it('re-fetches with the search term', async () => {
      const wrapper = mountView()
      await flushPromises()
      vi.mocked(getClientPortfolio).mockClear()

      const searchInput = wrapper
        .findAll('input')
        .find((i) => i.attributes('placeholder') === 'Naziv klijenta...')
      await searchInput!.setValue('Prime')
      await flushPromises()

      expect(getClientPortfolio).toHaveBeenCalledWith(
        1,
        expect.objectContaining({ search: 'Prime' }),
      )
    })

    it('re-fetches with the status filter', async () => {
      const wrapper = mountView()
      await flushPromises()
      vi.mocked(getClientPortfolio).mockClear()

      const selects = wrapper.findAll('select')
      // DOM order: staff-role select, connection-granted-role select, then
      // the portfolio's status filter — status filter is the third
      // <select> on the page (org().my_role is admin, so the
      // staff-invite form's select renders first). Sorting moved from a
      // combined ordering <select> to the DataTable's sortable column
      // headers, so this is the last select on the page now.
      await selects[2]!.setValue('critical')
      await flushPromises()

      expect(getClientPortfolio).toHaveBeenCalledWith(
        1,
        expect.objectContaining({ status: 'critical' }),
      )
    })

    it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
      vi.mocked(getClientPortfolio).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [portfolioRow()],
        summary: { total: 1, ok: 1, attention: 0, critical: 0 },
      })
      const wrapper = mountView()
      await flushPromises()
      vi.mocked(getClientPortfolio).mockClear()

      // The client-name column is the first sortable header (sortKey
      // 'name') — it's already sorted ascending by default (the old
      // ordering <select>'s "Naziv (A-Š)" default), so one click cycles
      // it to descending.
      await wrapper.find('th button').trigger('click')
      await flushPromises()

      expect(getClientPortfolio).toHaveBeenCalledWith(1, expect.objectContaining({ ordering: '-name' }))
    })

    it('clicking a row switches the active company and navigates home', async () => {
      vi.mocked(getClientPortfolio).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [portfolioRow({ company_id: 42 })],
        summary: { total: 1, ok: 1, attention: 0, critical: 0 },
      })
      const pushSpy = vi.spyOn(router, 'push')

      const wrapper = mountView()
      await flushPromises()
      const company = useCompanyStore()
      const setCurrentCompanySpy = vi.spyOn(company, 'setCurrentCompany')

      await wrapper.find('tbody tr').trigger('click')
      await flushPromises()

      expect(setCurrentCompanySpy).toHaveBeenCalledWith(42)
      expect(pushSpy).toHaveBeenCalledWith({ name: 'home' })
    })
  })
})
