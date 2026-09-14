import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Skeleton from '../Skeleton.vue'

describe('Skeleton', () => {
  it('renders a single pulsing bar by default', () => {
    const wrapper = mount(Skeleton)
    expect(wrapper.findAll('.animate-pulse')).toHaveLength(1)
  })

  it('respects the count prop', () => {
    const wrapper = mount(Skeleton, { props: { count: 3 } })
    expect(wrapper.findAll('.animate-pulse')).toHaveLength(3)
  })

  it('has an accessible loading role', () => {
    const wrapper = mount(Skeleton)
    expect(wrapper.attributes('role')).toBe('status')
  })
})
