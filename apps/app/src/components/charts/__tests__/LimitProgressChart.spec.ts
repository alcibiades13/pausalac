import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LimitProgressChart from '../LimitProgressChart.vue'
import { i18n } from '@/i18n'

describe('LimitProgressChart', () => {
  it('shows an empty state when there is no history', () => {
    const wrapper = mount(LimitProgressChart, {
      global: { plugins: [i18n] },
      props: { history: [], projection: [], threshold: '6000000.00', currency: 'RSD' },
    })
    expect(wrapper.text()).toContain('Još nema podataka za ovu godinu.')
    expect(wrapper.find('svg').exists()).toBe(false)
  })

  it('renders a single dot, no path, for one history point with no projection', () => {
    const wrapper = mount(LimitProgressChart, {
      global: { plugins: [i18n] },
      props: {
        history: [{ month: '2026-09-01', cumulative: '1000.00' }],
        projection: [],
        threshold: '6000000.00',
        currency: 'RSD',
      },
    })
    expect(wrapper.find('circle').exists()).toBe(true)
    expect(wrapper.find('path').exists()).toBe(false)
  })

  it('renders both a solid history path and a dashed projection path when projecting', () => {
    const wrapper = mount(LimitProgressChart, {
      global: { plugins: [i18n] },
      props: {
        history: [
          { month: '2026-07-01', cumulative: '1000.00' },
          { month: '2026-08-01', cumulative: '2000.00' },
          { month: '2026-09-01', cumulative: '3000.00' },
        ],
        projection: [
          { month: '2026-09-01', cumulative: '3000.00' },
          { month: '2026-10-01', cumulative: '4000.00' },
          { month: '2026-11-01', cumulative: '5000.00' },
          { month: '2026-12-01', cumulative: '6000.00' },
        ],
        threshold: '6000000.00',
        currency: 'RSD',
      },
    })
    const paths = wrapper.findAll('path')
    expect(paths.length).toBe(2)
    expect(paths[1]!.attributes('stroke-dasharray')).toBeTruthy()
  })

  it('always renders the threshold reference line', () => {
    const wrapper = mount(LimitProgressChart, {
      global: { plugins: [i18n] },
      props: {
        history: [{ month: '2026-09-01', cumulative: '1000.00' }],
        projection: [],
        threshold: '6000000.00',
        currency: 'RSD',
      },
    })
    expect(wrapper.text()).toContain('Limit')
  })
})
