import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
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
    const wrapper = mount(AdminTaxObligationsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('Na čekanju')
  })
})
