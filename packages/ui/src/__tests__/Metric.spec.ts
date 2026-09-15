import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Metric from '../Metric.vue'

describe('Metric', () => {
  it('renders the label and the default slot as the value', () => {
    const wrapper = mount(Metric, {
      props: { label: 'Fakturisano ove godine' },
      slots: { default: '2.840.000,00 RSD' },
    })
    expect(wrapper.text()).toContain('Fakturisano ove godine')
    expect(wrapper.text()).toContain('2.840.000,00 RSD')
  })

  it('does not render a secondary line when the slot is not provided', () => {
    const wrapper = mount(Metric, { props: { label: 'X' }, slots: { default: 'Y' } })
    expect(wrapper.findAll('div').length).toBe(1)
  })

  it('renders the secondary slot when provided', () => {
    const wrapper = mount(Metric, {
      props: { label: 'Neizmireno' },
      slots: { default: '100.000,00 RSD', secondary: '<p class="text-danger">od toga 1 kasni</p>' },
    })
    expect(wrapper.text()).toContain('od toga 1 kasni')
    expect(wrapper.find('.text-danger').exists()).toBe(true)
  })
})
