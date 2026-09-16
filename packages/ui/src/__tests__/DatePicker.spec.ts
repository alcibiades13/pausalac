import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DatePicker from '../DatePicker.vue'

describe('DatePicker', () => {
  it('displays a real ISO model value in fixed dd.mm.gggg. format, not the locale-dependent native one', () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-03-05' } })
    const decorative = wrapper.get('input[type="text"]')
    expect(decorative.element.value).toBe('05.03.2026.')
  })

  it('shows an empty display value when the model is empty', () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '' } })
    const decorative = wrapper.get('input[type="text"]')
    expect(decorative.element.value).toBe('')
  })

  it('the real date input carries the raw ISO value for the browser picker, and is the only focusable control', () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '2026-03-05' } })
    const dateInput = wrapper.get('input[type="date"]')
    expect(dateInput.element.value).toBe('2026-03-05')
    const decorative = wrapper.get('input[type="text"]')
    expect(decorative.attributes('tabindex')).toBe('-1')
  })

  it('emits update:modelValue as the real date input changes', async () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '' } })
    const dateInput = wrapper.get('input[type="date"]')
    await dateInput.setValue('2026-12-31')
    expect(wrapper.emitted('update:modelValue')).toEqual([['2026-12-31']])
  })

  it('associates the label with the real date input, not the decorative text field', () => {
    const wrapper = mount(DatePicker, { props: { modelValue: '', label: 'Datum od' } })
    const label = wrapper.get('label')
    const dateInput = wrapper.get('input[type="date"]')
    expect(label.attributes('for')).toBe(dateInput.attributes('id'))
  })
})
