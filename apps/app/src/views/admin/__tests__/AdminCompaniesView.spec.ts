import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdminCompaniesView from '../AdminCompaniesView.vue'
import { listAdminCompanies, listAdminCompanyMembers } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminCompanies: vi.fn<typeof listAdminCompanies>(),
  listAdminCompanyMembers: vi.fn<typeof listAdminCompanyMembers>(),
}))

describe('AdminCompaniesView', () => {
  beforeEach(() => {
    vi.mocked(listAdminCompanies).mockReset()
    vi.mocked(listAdminCompanyMembers).mockReset()
  })

  it('renders companies returned by the service', async () => {
    vi.mocked(listAdminCompanies).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          name: 'Firma A',
          legal_name: '',
          pib: '111111111',
          city: 'Beograd',
          country: 'RS',
          is_active: true,
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminCompaniesView)
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
  })

  it('loads and displays members when "Članovi" is clicked', async () => {
    vi.mocked(listAdminCompanies).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          name: 'Firma A',
          legal_name: '',
          pib: '111111111',
          city: 'Beograd',
          country: 'RS',
          is_active: true,
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    vi.mocked(listAdminCompanyMembers).mockResolvedValue([
      { user_email: 'vlasnik@pausalac.rs', role: 'owner', status: 'active' },
    ])

    const wrapper = mount(AdminCompaniesView)
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(listAdminCompanyMembers).toHaveBeenCalledWith(1)
    expect(wrapper.text()).toContain('vlasnik@pausalac.rs')
  })
})
