import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MoneyInput from '../MoneyInput.vue'

describe('MoneyInput', () => {
  it('renders a numeric input with decimal-friendly defaults', () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '' } })
    const input = wrapper.get('input')
    expect(input.attributes('type')).toBe('number')
    expect(input.attributes('step')).toBe('0.01')
    expect(input.attributes('min')).toBe('0')
  })

  it('shows the currency suffix, defaulting to RSD', () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '' } })
    expect(wrapper.text()).toContain('RSD')
  })

  it('shows a custom currency suffix when provided', () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '', currency: 'EUR' } })
    expect(wrapper.text()).toContain('EUR')
  })

  it('associates the label with the input', () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '', label: 'Iznos' } })
    const input = wrapper.get('input')
    const label = wrapper.get('label')
    expect(label.attributes('for')).toBe(input.attributes('id'))
  })

  it('emits update:modelValue as the user types', async () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '' } })
    await wrapper.get('input').setValue('1500.50')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['1500.50'])
  })

  it('sets aria-invalid and renders the error message when error is provided', () => {
    const wrapper = mount(MoneyInput, { props: { modelValue: '', error: 'Iznos je obavezan.' } })
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('true')
    expect(wrapper.text()).toContain('Iznos je obavezan.')
  })
})
