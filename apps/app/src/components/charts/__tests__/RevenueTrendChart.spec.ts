import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RevenueTrendChart from '../RevenueTrendChart.vue'
import { i18n } from '@/i18n'
import type { MonthlyRevenuePoint } from '@/services/analytics'

function point(month: string, amount: string): MonthlyRevenuePoint {
  return { month, amount }
}

describe('RevenueTrendChart', () => {
  it('shows an empty state when there is no data', () => {
    const wrapper = mount(RevenueTrendChart, {
      global: { plugins: [i18n] },
      props: { series: [], currency: 'RSD' },
    })
    expect(wrapper.text()).toContain('Još nema podataka o prihodu.')
    expect(wrapper.find('svg').exists()).toBe(false)
  })

  it('renders a dot and flat baseline, not a broken area, for a single data point', () => {
    const wrapper = mount(RevenueTrendChart, {
      global: { plugins: [i18n] },
      props: { series: [point('2026-09-01', '1000.00')], currency: 'RSD' },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.find('circle').exists()).toBe(true)
    expect(wrapper.find('path').exists()).toBe(false)
  })

  it('renders a shaded area and line for multiple points, including a negative (storno) month', () => {
    const wrapper = mount(RevenueTrendChart, {
      global: { plugins: [i18n] },
      props: {
        series: [point('2026-07-01', '1000.00'), point('2026-08-01', '-200.00'), point('2026-09-01', '500.00')],
        currency: 'RSD',
      },
    })
    const paths = wrapper.findAll('path')
    // one filled area path + one stroked line path
    expect(paths.length).toBe(2)
  })

  it('drops zero-filled future months instead of rendering them as if they were known', () => {
    const wrapper = mount(RevenueTrendChart, {
      global: { plugins: [i18n] },
      props: {
        // A year far enough out that "today" (whenever this test runs)
        // is always before it — the backend zero-fills through
        // year-end, but an unearned future month must never render
        // identically to a real past month with zero revenue.
        series: [point('2020-01-01', '1000.00'), point('2099-01-01', '0.00')],
        currency: 'RSD',
      },
    })
    // Only the one real (past) point remains -> single-point rendering,
    // not a two-point line that would imply the future month is known.
    expect(wrapper.find('circle').exists()).toBe(true)
    expect(wrapper.find('path').exists()).toBe(false)
    expect(wrapper.findAll('text').length).toBe(1)
  })
})
