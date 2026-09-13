import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MoneyDisplay from '../MoneyDisplay.vue'

describe('MoneyDisplay', () => {
  it('formats a whole number with Serbian thousands separators', () => {
    const wrapper = mount(MoneyDisplay, { props: { amount: '2840000', currency: 'RSD' } })
    expect(wrapper.text()).toBe('2.840.000,00 RSD')
  })

  it('formats a decimal string with a comma decimal separator', () => {
    const wrapper = mount(MoneyDisplay, { props: { amount: '1500.5', currency: 'EUR' } })
    expect(wrapper.text()).toBe('1.500,50 EUR')
  })

  it('accepts a numeric amount as well as a string', () => {
    const wrapper = mount(MoneyDisplay, { props: { amount: 1000, currency: 'RSD' } })
    expect(wrapper.text()).toBe('1.000,00 RSD')
  })

  it('renders negative amounts with a minus sign', () => {
    const wrapper = mount(MoneyDisplay, { props: { amount: '-500', currency: 'RSD' } })
    expect(wrapper.text()).toContain('-500,00 RSD')
  })

  it('switches to compact notation when compact is set', () => {
    const wrapper = mount(MoneyDisplay, { props: { amount: '2840000', currency: 'RSD', compact: true } })
    expect(wrapper.text()).not.toContain('2.840.000')
    expect(wrapper.text()).toContain('RSD')
  })
})
