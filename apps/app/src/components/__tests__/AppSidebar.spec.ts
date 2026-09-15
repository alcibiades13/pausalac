import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppSidebar from '../AppSidebar.vue'

describe('AppSidebar', () => {
  it('is hidden below sm and a flex column from sm up', () => {
    const wrapper = mount(AppSidebar)
    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('hidden')
    expect(aside.classes()).toContain('sm:flex')
    expect(aside.classes()).toContain('flex-col')
  })

  it('renders the header, default, and footer slots in their own regions', () => {
    const wrapper = mount(AppSidebar, {
      slots: {
        header: '<span class="the-header">Logo</span>',
        default: '<a class="the-link">Početna</a>',
        footer: '<button class="the-footer">Odjavi se</button>',
      },
    })

    expect(wrapper.find('.the-header').exists()).toBe(true)
    expect(wrapper.find('.the-link').exists()).toBe(true)
    expect(wrapper.find('.the-footer').exists()).toBe(true)
  })

  it('labels the nav landmark, defaulting to "Glavna navigacija"', () => {
    const wrapper = mount(AppSidebar)
    expect(wrapper.get('nav').attributes('aria-label')).toBe('Glavna navigacija')
  })

  it('accepts a custom nav label', () => {
    const wrapper = mount(AppSidebar, { props: { navLabel: 'Admin navigacija' } })
    expect(wrapper.get('nav').attributes('aria-label')).toBe('Admin navigacija')
  })
})
