import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Pagination from '../Pagination.vue'

describe('Pagination', () => {
  it('renders nothing when there is only one page', () => {
    const wrapper = mount(Pagination, { props: { hasNext: false, hasPrevious: false } })
    expect(wrapper.find('nav').exists()).toBe(false)
  })

  it('renders Prethodna/Sledeća when there are more pages', () => {
    const wrapper = mount(Pagination, { props: { hasNext: true, hasPrevious: false } })
    expect(wrapper.text()).toContain('Prethodna')
    expect(wrapper.text()).toContain('Sledeća')
  })

  it('disables Prethodna when hasPrevious is false and Sledeća when hasNext is false', () => {
    const wrapper = mount(Pagination, { props: { hasNext: false, hasPrevious: true } })
    const buttons = wrapper.findAll('button')
    const prev = buttons.find((b) => b.text() === 'Prethodna')!
    const next = buttons.find((b) => b.text() === 'Sledeća')!
    expect(prev.attributes('disabled')).toBeUndefined()
    expect(next.attributes('disabled')).toBeDefined()
  })

  it('emits next/previous when the buttons are clicked', async () => {
    const wrapper = mount(Pagination, { props: { hasNext: true, hasPrevious: true } })
    await wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!.trigger('click')
    await wrapper.findAll('button').find((b) => b.text() === 'Prethodna')!.trigger('click')
    expect(wrapper.emitted('next')).toHaveLength(1)
    expect(wrapper.emitted('previous')).toHaveLength(1)
  })

  it('shows "Strana X od Y" when page/totalPages are given', () => {
    const wrapper = mount(Pagination, {
      props: { hasNext: true, hasPrevious: true, page: 2, totalPages: 5 },
    })
    expect(wrapper.text()).toContain('Strana 2 od 5')
  })

  it('omits the page indicator when page/totalPages are not given', () => {
    const wrapper = mount(Pagination, { props: { hasNext: true, hasPrevious: true } })
    expect(wrapper.text()).not.toContain('Strana')
  })
})
