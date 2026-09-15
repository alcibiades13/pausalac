import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from '../Input.vue'

describe('Input', () => {
  it('emits update:modelValue as the user types', async () => {
    const wrapper = mount(Input, { props: { modelValue: '' } })
    const input = wrapper.find('input')
    await input.setValue('marko@pausalac.rs')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['marko@pausalac.rs'])
  })

  it('renders the label and marks required fields', () => {
    const wrapper = mount(Input, { props: { label: 'Email', required: true } })
    expect(wrapper.text()).toContain('Email')
    expect(wrapper.find('input').attributes('required')).toBeDefined()
  })

  it('shows the error message instead of the hint when both are given', () => {
    const wrapper = mount(Input, { props: { error: 'Obavezno polje.', hint: 'npr. ime@firma.rs' } })
    expect(wrapper.text()).toContain('Obavezno polje.')
    expect(wrapper.text()).not.toContain('npr. ime@firma.rs')
  })

  it('marks aria-invalid when there is an error', () => {
    const wrapper = mount(Input, { props: { error: 'Greška.' } })
    expect(wrapper.find('input').attributes('aria-invalid')).toBe('true')
  })

  it('keeps the emitted value a string for type="number", not a JS number', async () => {
    // Vue 3.4+ auto-casts v-model on type="number" inputs to a JS
    // number, which would silently break this app's Decimal-as-string
    // convention for every money/numeric field using this component.
    const wrapper = mount(Input, { props: { modelValue: '', type: 'number' } })
    await wrapper.find('input').setValue('1500.50')
    const emitted = wrapper.emitted('update:modelValue')?.[0]?.[0]
    expect(emitted).toBe('1500.50')
    expect(typeof emitted).toBe('string')
  })
})
