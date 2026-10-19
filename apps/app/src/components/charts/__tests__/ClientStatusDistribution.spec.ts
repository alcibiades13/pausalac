import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ClientStatusDistribution from '../ClientStatusDistribution.vue'
import { i18n } from '@/i18n'

describe('ClientStatusDistribution', () => {
  it('shows an empty state when no clients are connected yet', () => {
    const wrapper = mount(ClientStatusDistribution, {
      global: { plugins: [i18n] },
      props: { summary: { total: 0, ok: 0, attention: 0, critical: 0 } },
    })
    expect(wrapper.text()).toContain('Još nema povezanih klijenata.')
    expect(wrapper.find('[data-testid="apexchart-stub"]').exists()).toBe(false)
  })

  it('renders the ok/attention/critical counts as the donut series', () => {
    const wrapper = mount(ClientStatusDistribution, {
      global: { plugins: [i18n] },
      props: { summary: { total: 6, ok: 3, attention: 2, critical: 1 } },
    })
    const stub = wrapper.find('[data-testid="apexchart-stub"]')
    expect(stub.exists()).toBe(true)
    const series = JSON.parse(stub.attributes('data-series')!)
    expect(series).toEqual([3, 2, 1])
  })
})
