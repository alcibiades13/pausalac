import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InvoiceStatusBadge from '../InvoiceStatusBadge.vue'
import { i18n } from '@/i18n'

describe('InvoiceStatusBadge', () => {
  it('renders the Serbian label for draft', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'draft' }, global: { plugins: [i18n] } })
    expect(wrapper.text()).toBe('Nacrt')
  })

  it('renders the Serbian label for issued', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'issued' }, global: { plugins: [i18n] } })
    expect(wrapper.text()).toBe('Izdata')
  })

  it('renders the Serbian label for cancelled', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'cancelled' }, global: { plugins: [i18n] } })
    expect(wrapper.text()).toBe('Stornirana')
  })

  it('renders the Serbian label for overdue with the danger variant', () => {
    const wrapper = mount(InvoiceStatusBadge, { props: { status: 'overdue' }, global: { plugins: [i18n] } })
    expect(wrapper.text()).toBe('Kasni')
    expect(wrapper.classes().join(' ')).toContain('text-danger')
  })
})
