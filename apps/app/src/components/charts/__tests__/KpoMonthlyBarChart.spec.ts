import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import KpoMonthlyBarChart from '../KpoMonthlyBarChart.vue'
import { i18n } from '@/i18n'
import type { KpoMonthlySummaryRow } from '@/services/kpo'

function row(month: string, products: string, services: string): KpoMonthlySummaryRow {
  return { month, products, services, total: String(Number(products) + Number(services)) }
}

describe('KpoMonthlyBarChart', () => {
  it('shows an empty state when every month is zero (new company)', () => {
    const wrapper = mount(KpoMonthlyBarChart, {
      global: { plugins: [i18n] },
      props: {
        rows: [row('2026-01-01', '0.00', '0.00'), row('2026-02-01', '0.00', '0.00')],
        currency: 'RSD',
      },
    })
    expect(wrapper.text()).toContain('Još nema KPO prometa ove godine.')
    expect(wrapper.find('[data-testid="apexchart-stub"]').exists()).toBe(false)
  })

  it('renders the bar chart with products/services series when there is activity', () => {
    const wrapper = mount(KpoMonthlyBarChart, {
      global: { plugins: [i18n] },
      props: {
        rows: [row('2026-01-01', '500.00', '0.00'), row('2026-02-01', '0.00', '1500.00')],
        currency: 'RSD',
      },
    })
    const stub = wrapper.find('[data-testid="apexchart-stub"]')
    expect(stub.exists()).toBe(true)
    expect(stub.attributes('data-type')).toBe('bar')
    const series = JSON.parse(stub.attributes('data-series')!)
    expect(series).toEqual([
      { name: 'Proizvodi', data: [500, 0] },
      { name: 'Usluge', data: [0, 1500] },
    ])
  })
})
