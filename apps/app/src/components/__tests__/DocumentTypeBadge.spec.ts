import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DocumentTypeBadge from '../DocumentTypeBadge.vue'

describe('DocumentTypeBadge', () => {
  it('renders the Serbian label for invoice', () => {
    const wrapper = mount(DocumentTypeBadge, { props: { type: 'invoice' } })
    expect(wrapper.text()).toBe('Faktura')
  })

  it('renders the Serbian label for profaktura', () => {
    const wrapper = mount(DocumentTypeBadge, { props: { type: 'profaktura' } })
    expect(wrapper.text()).toBe('Profaktura')
  })

  it('renders the Serbian label for avans', () => {
    const wrapper = mount(DocumentTypeBadge, { props: { type: 'avans' } })
    expect(wrapper.text()).toBe('Avansni račun')
  })
})
