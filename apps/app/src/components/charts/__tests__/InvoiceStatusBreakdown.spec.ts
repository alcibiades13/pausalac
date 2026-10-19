import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InvoiceStatusBreakdown from '../InvoiceStatusBreakdown.vue'
import { i18n } from '@/i18n'

describe('InvoiceStatusBreakdown', () => {
  it('shows an empty state when nothing has been invoiced this year', () => {
    const wrapper = mount(InvoiceStatusBreakdown, {
      global: { plugins: [i18n] },
      props: {
        breakdown: { count: 0, total: '0.00', currency: 'RSD', overdue_count: 0, overdue_total: '0.00', paid_ytd: '0.00' },
      },
    })
    expect(wrapper.text()).toContain('Još nema faktura ove godine.')
    expect(wrapper.find('[data-testid="apexchart-stub"]').exists()).toBe(false)
  })

  it('splits total into pending/overdue and includes paid YTD as a separate slice', () => {
    const wrapper = mount(InvoiceStatusBreakdown, {
      global: { plugins: [i18n] },
      props: {
        breakdown: {
          count: 2,
          total: '1500.00',
          currency: 'RSD',
          overdue_count: 1,
          overdue_total: '500.00',
          paid_ytd: '1000.00',
        },
      },
    })
    const stub = wrapper.find('[data-testid="apexchart-stub"]')
    expect(stub.exists()).toBe(true)
    const series = JSON.parse(stub.attributes('data-series')!)
    // [paid, pending, overdue]
    expect(series).toEqual([1000, 1000, 500])
  })
})
