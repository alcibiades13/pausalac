import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Progress from '../Progress.vue'

describe('Progress', () => {
  it('exposes progressbar semantics with the current/min/max values', () => {
    const wrapper = mount(Progress, { props: { value: 47 } })
    const bar = wrapper.get('[role="progressbar"]')
    expect(bar.attributes('aria-valuenow')).toBe('47')
    expect(bar.attributes('aria-valuemin')).toBe('0')
    expect(bar.attributes('aria-valuemax')).toBe('100')
  })

  it('renders the inner bar width proportional to value/max', () => {
    const wrapper = mount(Progress, { props: { value: 25, max: 50 } })
    const inner = wrapper.find('[role="progressbar"] > div')
    expect(inner.attributes('style')).toContain('width: 50%')
  })

  it('clamps width to 100% when value exceeds max', () => {
    const wrapper = mount(Progress, { props: { value: 999, max: 100 } })
    const inner = wrapper.find('[role="progressbar"] > div')
    expect(inner.attributes('style')).toContain('width: 100%')
  })

  it('clamps width to 0% when value is negative', () => {
    const wrapper = mount(Progress, { props: { value: -10 } })
    const inner = wrapper.find('[role="progressbar"] > div')
    expect(inner.attributes('style')).toContain('width: 0%')
  })

  it('applies the danger variant color', () => {
    const wrapper = mount(Progress, { props: { value: 90, variant: 'danger' } })
    const inner = wrapper.find('[role="progressbar"] > div')
    expect(inner.classes()).toContain('bg-danger')
  })

  it('defaults to the primary variant color, using the darker shade for visibility', () => {
    // Not `bg-primary` — --color-primary is a pale, user-specified
    // violet (tokens.css) that would barely show up as a thin fill;
    // `primary-dark` is the same hue family but actually visible.
    const wrapper = mount(Progress, { props: { value: 10 } })
    const inner = wrapper.find('[role="progressbar"] > div')
    expect(inner.classes()).toContain('bg-primary-dark')
  })

  it('sets an aria-label when provided', () => {
    const wrapper = mount(Progress, { props: { value: 47, label: 'Paušalni limit' } })
    expect(wrapper.get('[role="progressbar"]').attributes('aria-label')).toBe('Paušalni limit')
  })
})
