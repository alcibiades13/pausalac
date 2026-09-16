import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DropdownMenu from '../DropdownMenu.vue'

function mountMenu() {
  return mount(DropdownMenu, {
    props: { label: 'Test menu' },
    slots: {
      trigger: '<span>Open</span>',
      default: '<button type="button">Item one</button>',
    },
    attachTo: document.body,
  })
}

describe('DropdownMenu', () => {
  it('starts closed and opens on trigger click', async () => {
    const wrapper = mountMenu()
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)

    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Item one')

    wrapper.unmount()
  })

  it('closes on Escape', async () => {
    const wrapper = mountMenu()
    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)

    await wrapper.get('[role="menu"]').trigger('keydown', { key: 'Escape' })
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)

    wrapper.unmount()
  })

  it('closes on an outside click', async () => {
    const wrapper = mountMenu()
    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)

    document.body.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)

    wrapper.unmount()
  })

  it('applies the given menu width class', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { label: 'Test menu', menuWidthClass: 'w-64' },
      slots: { trigger: '<span>Open</span>' },
    })
    await wrapper.get('button[aria-haspopup="menu"]').trigger('click')
    expect(wrapper.get('[role="menu"]').classes()).toContain('w-64')
  })
})
