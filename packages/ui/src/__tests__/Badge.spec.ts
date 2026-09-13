import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Badge from '../Badge.vue'

describe('Badge', () => {
  it('renders slot content', () => {
    const wrapper = mount(Badge, { slots: { default: 'Nacrt' } })
    expect(wrapper.text()).toBe('Nacrt')
  })

  it('defaults to the neutral variant', () => {
    const wrapper = mount(Badge)
    expect(wrapper.classes().join(' ')).toContain('text-text-secondary')
  })

  it('applies the danger variant classes', () => {
    const wrapper = mount(Badge, { props: { variant: 'danger' } })
    expect(wrapper.classes().join(' ')).toContain('text-danger')
  })
})
