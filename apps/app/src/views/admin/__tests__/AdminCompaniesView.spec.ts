import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
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
    const wrapper = mount(AdminCompaniesView, { global: { plugins: [i18n] } })
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

    const wrapper = mount(AdminCompaniesView, { global: { plugins: [i18n] } })
    await flushPromises()
    // `th button` (the new sortable column header) is now the first
    // `<button>` on the page — target the row action button by its
    // text instead of position.
    await wrapper.findAll('button').find((b) => b.text() === 'Članovi')!.trigger('click')
    await flushPromises()

    expect(listAdminCompanyMembers).toHaveBeenCalledWith(1)
    expect(wrapper.text()).toContain('vlasnik@pausalac.rs')
  })

  it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
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
    const wrapper = mount(AdminCompaniesView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('th button').trigger('click')
    await flushPromises()

    expect(listAdminCompanies).toHaveBeenLastCalledWith(expect.objectContaining({ ordering: 'name' }))
  })

  it('shows the current page and total page count', async () => {
    vi.mocked(listAdminCompanies).mockResolvedValue({
      count: 60,
      next: 'http://api/admin/companies/?page=2',
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
    const wrapper = mount(AdminCompaniesView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Strana 1 od 3')

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    await nextButton.trigger('click')
    await flushPromises()

    expect(listAdminCompanies).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
