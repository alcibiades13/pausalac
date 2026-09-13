import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InvoiceStatusBadge from '../InvoiceStatusBadge.vue'

describe('InvoiceStatusBadge', () => {
  it('renders the Serbian label for draft', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'draft' } })
    expect(wrapper.text()).toBe('Nacrt')
  })

  it('renders the Serbian label for issued', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'issued' } })
    expect(wrapper.text()).toBe('Izdata')
  })

  it('renders the Serbian label for cancelled', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'cancelled' } })
    expect(wrapper.text()).toBe('Stornirana')
  })

  it('renders the Serbian label for overdue with the danger variant', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'overdue' } })
    expect(wrapper.text()).toBe('Kasni')
    expect(wrapper.classes().join(' ')).toContain('text-danger')
  })
})
