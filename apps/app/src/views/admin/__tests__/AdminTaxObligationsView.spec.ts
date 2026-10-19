import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminTaxObligationsView from '../AdminTaxObligationsView.vue'
import { listAdminTaxObligations } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminTaxObligations: vi.fn<typeof listAdminTaxObligations>(),
}))

describe('AdminTaxObligationsView', () => {
  beforeEach(() => {
    vi.mocked(listAdminTaxObligations).mockReset()
  })

  it('renders tax obligations returned by the service', async () => {
    vi.mocked(listAdminTaxObligations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          period_start: '2026-01-01',
          due_date: '2026-02-15',
          total_amount: '400.00',
          status: 'pending',
          paid_at: null,
        },
      ],
    })
    const wrapper = mount(AdminTaxObligationsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('Na čekanju')
  })

  it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
    vi.mocked(listAdminTaxObligations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          period_start: '2026-01-01',
          due_date: '2026-02-15',
          total_amount: '400.00',
          status: 'pending',
          paid_at: null,
        },
      ],
    })
    const wrapper = mount(AdminTaxObligationsView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('th button').trigger('click')
    await flushPromises()

    expect(listAdminTaxObligations).toHaveBeenLastCalledWith(
      expect.objectContaining({ ordering: 'period_start' }),
    )
  })

  it('shows the current page and total page count', async () => {
    vi.mocked(listAdminTaxObligations).mockResolvedValue({
      count: 60,
      next: 'http://api/admin/tax-obligations/?page=2',
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          period_start: '2026-01-01',
          due_date: '2026-02-15',
          total_amount: '400.00',
          status: 'pending',
          paid_at: null,
        },
      ],
    })
    const wrapper = mount(AdminTaxObligationsView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Strana 1 od 3')

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    await nextButton.trigger('click')
    await flushPromises()

    expect(listAdminTaxObligations).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
