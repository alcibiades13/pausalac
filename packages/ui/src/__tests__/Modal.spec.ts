import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '../Modal.vue'

describe('Modal', () => {
  it('renders nothing when closed', () => {
    mount(Modal, { props: { open: false, title: 'Naslov' } })
    expect(document.querySelector('[role="dialog"]')).toBeFalsy()
  })

  it('renders dialog semantics and the title when open', () => {
    const wrapper = mount(Modal, {
      props: { open: true, title: 'Obriši dokument?' },
      slots: { default: 'Ova radnja se ne može opozvati.' },
    })
    const dialog = document.querySelector('[role="dialog"]')!
    expect(dialog.getAttribute('aria-modal')).toBe('true')
    expect(dialog.textContent).toContain('Obriši dokument?')
    expect(dialog.textContent).toContain('Ova radnja se ne može opozvati.')
    wrapper.unmount()
  })

  it('emits update:open false when the close button is clicked', async () => {
    const wrapper = mount(Modal, { props: { open: true, title: 'X' } })
    const closeButton = document.querySelector<HTMLElement>('[aria-label="Zatvori"]')!
    closeButton.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
    wrapper.unmount()
  })

  it('emits update:open false when the backdrop is clicked', async () => {
    const wrapper = mount(Modal, { props: { open: true, title: 'X' } })
    const backdrop = document.querySelector<HTMLElement>('.fixed.inset-0 > .bg-navy\\/40')!
    backdrop.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
    wrapper.unmount()
  })

  it('renders a footer slot when provided', () => {
    const wrapper = mount(Modal, {
      props: { open: true, title: 'X' },
      slots: { footer: '<button class="confirm-btn">Potvrdi</button>' },
    })
    expect(document.querySelector('.confirm-btn')).toBeTruthy()
    wrapper.unmount()
  })
})
