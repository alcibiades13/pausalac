import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '../EmptyState.vue'

describe('EmptyState', () => {
  it('renders title and description', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Još nemaš klijente.', description: 'Dodaj prvog klijenta da počneš.' },
    })
    expect(wrapper.text()).toContain('Još nemaš klijente.')
    expect(wrapper.text()).toContain('Dodaj prvog klijenta da počneš.')
  })

  it('renders the action slot when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Prazno' },
      slots: { action: '<button>Novi klijent</button>' },
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('omits the action wrapper when no action slot is given', () => {
    const wrapper = mount(EmptyState, { props: { title: 'Prazno' } })
    expect(wrapper.find('button').exists()).toBe(false)
  })
})
