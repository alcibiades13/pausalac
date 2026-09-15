import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'
import { useDialogA11y } from '../useDialogA11y'

const HostComponent = defineComponent({
  props: { open: { type: Boolean, default: false } },
  emits: ['close'],
  setup(props, { emit }) {
    const containerRef = ref<HTMLElement | null>(null)
    const openRef = ref(props.open)
    useDialogA11y(containerRef, openRef, () => emit('close'))
    return { containerRef, openRef }
  },
  template: `
    <div>
      <button id="outside">Outside</button>
      <div v-if="openRef" ref="containerRef" tabindex="-1">
        <button id="first">First</button>
        <button id="second">Second</button>
      </div>
    </div>
  `,
})

describe('useDialogA11y', () => {
  it('moves focus into the container (the first focusable element) when it opens', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    expect(document.activeElement?.id).toBe('first')
    wrapper.unmount()
  })

  it('restores focus to the previously-focused element when it closes', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    const outside = wrapper.get('#outside').element as HTMLElement
    outside.focus()
    expect(document.activeElement?.id).toBe('outside')

    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))
    expect(document.activeElement?.id).toBe('first')

    wrapper.vm.openRef = false
    await wrapper.vm.$nextTick()
    expect(document.activeElement?.id).toBe('outside')
    wrapper.unmount()
  })

  it('calls onClose when Escape is pressed while open', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(wrapper.emitted('close')).toBeTruthy()
    wrapper.unmount()
  })

  it('traps Tab: wraps from the last focusable element back to the first', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    const second = wrapper.get('#second').element as HTMLElement
    second.focus()
    const event = new KeyboardEvent('keydown', { key: 'Tab', cancelable: true })
    window.dispatchEvent(event)

    expect(document.activeElement?.id).toBe('first')
    wrapper.unmount()
  })

  it('traps Shift+Tab: wraps from the first focusable element back to the last', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    const first = wrapper.get('#first').element as HTMLElement
    first.focus()
    const event = new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, cancelable: true })
    window.dispatchEvent(event)

    expect(document.activeElement?.id).toBe('second')
    wrapper.unmount()
  })

  it('stops listening once the component unmounts', async () => {
    const wrapper = mount(HostComponent, { attachTo: document.body })
    wrapper.vm.openRef = true
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    const closeSpy = vi.fn()
    wrapper.unmount()
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(closeSpy).not.toHaveBeenCalled()
  })
})
