import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminInvoicesView from '../AdminInvoicesView.vue'
import { listAdminInvoices } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminInvoices: vi.fn<typeof listAdminInvoices>(),
}))

describe('AdminInvoicesView', () => {
  beforeEach(() => {
    vi.mocked(listAdminInvoices).mockReset()
  })

  it('renders invoices returned by the service', async () => {
    vi.mocked(listAdminInvoices).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          client_name: 'Klijent A',
          invoice_number: '2026-0001',
          status: 'sent',
          issue_date: '2026-01-01',
          due_date: '2026-01-15',
          total: '1500.00',
          currency: 'RSD',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminInvoicesView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('Klijent A')
    expect(wrapper.text()).toContain('2026-0001')
  })

  it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
    vi.mocked(listAdminInvoices).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          client_name: 'Klijent A',
          invoice_number: '2026-0001',
          status: 'sent',
          issue_date: '2026-01-01',
          due_date: '2026-01-15',
          total: '1500.00',
          currency: 'RSD',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminInvoicesView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('th button').trigger('click')
    await flushPromises()

    expect(listAdminInvoices).toHaveBeenLastCalledWith(expect.objectContaining({ ordering: 'due_date' }))
  })

  it('shows the current page and total page count', async () => {
    vi.mocked(listAdminInvoices).mockResolvedValue({
      count: 60,
      next: 'http://api/admin/invoices/?page=2',
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          client_name: 'Klijent A',
          invoice_number: '2026-0001',
          status: 'sent',
          issue_date: '2026-01-01',
          due_date: '2026-01-15',
          total: '1500.00',
          currency: 'RSD',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminInvoicesView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Strana 1 od 3')

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    await nextButton.trigger('click')
    await flushPromises()

    expect(listAdminInvoices).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
