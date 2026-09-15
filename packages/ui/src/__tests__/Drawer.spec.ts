import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Drawer from '../Drawer.vue'

describe('Drawer', () => {
  it('renders nothing when closed', () => {
    mount(Drawer, { props: { open: false, label: 'Brza akcija' } })
    expect(document.querySelector('[role="dialog"]')).toBeFalsy()
  })

  it('renders dialog semantics and slot content when open', () => {
    const wrapper = mount(Drawer, {
      props: { open: true, label: 'Brza akcija' },
      slots: { default: '<a href="/x">Nova faktura</a>' },
    })
    const dialog = document.querySelector('[role="dialog"]')!
    expect(dialog.getAttribute('aria-modal')).toBe('true')
    expect(dialog.getAttribute('aria-label')).toBe('Brza akcija')
    expect(dialog.textContent).toContain('Nova faktura')
    wrapper.unmount()
  })

  it('emits update:open false when the backdrop is clicked', async () => {
    const wrapper = mount(Drawer, { props: { open: true, label: 'X' } })
    const backdrop = document.querySelector<HTMLElement>('.fixed.inset-0.z-30 > .bg-navy\\/40')!
    backdrop.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
    wrapper.unmount()
  })

  it('applies an extra containerClass to the outer overlay when provided', () => {
    const wrapper = mount(Drawer, { props: { open: true, label: 'X', containerClass: 'sm:hidden' } })
    expect(document.querySelector('.fixed.inset-0.z-30.sm\\:hidden')).toBeTruthy()
    wrapper.unmount()
  })
})
