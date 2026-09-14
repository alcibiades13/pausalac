import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AccountingOrganizationView from '../AccountingOrganizationView.vue'
import {
  listOrganizations,
  createOrganization,
  listOrgStaff,
  addOrgStaff,
  removeOrgStaff,
  listOrgConnections,
  createOrgConnection,
  type AccountingOrganization,
  type OrgStaffMembership,
  type OrganizationConnection,
} from '@/services/accounting'

vi.mock('@/services/accounting', () => ({
  listOrganizations: vi.fn<typeof listOrganizations>(),
  createOrganization: vi.fn<typeof createOrganization>(),
  listOrgStaff: vi.fn<typeof listOrgStaff>(),
  addOrgStaff: vi.fn<typeof addOrgStaff>(),
  removeOrgStaff: vi.fn<typeof removeOrgStaff>(),
  listOrgConnections: vi.fn<typeof listOrgConnections>(),
  createOrgConnection: vi.fn<typeof createOrgConnection>(),
}))

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

describe('AccountingOrganizationView', () => {
  beforeEach(() => {
    vi.mocked(listOrganizations).mockReset()
    vi.mocked(createOrganization).mockReset()
    vi.mocked(listOrgStaff).mockReset()
    vi.mocked(addOrgStaff).mockReset()
    vi.mocked(removeOrgStaff).mockReset()
    vi.mocked(listOrgConnections).mockReset()
    vi.mocked(createOrgConnection).mockReset()
  })

  it('shows the create-organization form when the user has none', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(AccountingOrganizationView)
    await flushPromises()
    expect(wrapper.text()).toContain('Osnuj agenciju')
  })

  it('creates an organization and switches to the org view', async () => {
    vi.mocked(listOrganizations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(createOrganization).mockResolvedValue(org())

    const wrapper = mount(AccountingOrganizationView)
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

    const wrapper = mount(AccountingOrganizationView)
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

    const wrapper = mount(AccountingOrganizationView)
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

    const wrapper = mount(AccountingOrganizationView)
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

    const wrapper = mount(AccountingOrganizationView)
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
})
