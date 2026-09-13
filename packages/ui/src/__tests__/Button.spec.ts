import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '../Button.vue'

describe('Button', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, { slots: { default: 'Sačuvaj' } })
    expect(wrapper.text()).toBe('Sačuvaj')
  })

  it('is disabled while loading', () => {
    const wrapper = mount(Button, { props: { loading: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('is disabled when disabled prop is set', () => {
    const wrapper = mount(Button, { props: { disabled: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('is not disabled by default', () => {
    const wrapper = mount(Button)
    expect(wrapper.attributes('disabled')).toBeUndefined()
  })

  it('defaults to type=button so it never accidentally submits a form', () => {
    const wrapper = mount(Button)
    expect(wrapper.attributes('type')).toBe('button')
  })
})
