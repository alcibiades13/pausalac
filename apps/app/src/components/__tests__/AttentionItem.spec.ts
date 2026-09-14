import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import AttentionItem from '../AttentionItem.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
  ],
})

describe('AttentionItem', () => {
  it('renders the message and links to the given route', async () => {
    await router.push('/')
    const wrapper = mount(AttentionItem, {
      global: { plugins: [router] },
      props: {
        item: {
          type: 'overdue_invoices',
          message: '2 faktura(e) kasni sa ukupno 1.000,00 RSD potraživanja.',
          action: { route: 'invoices', query: { status: 'overdue' } },
        },
      },
    })
    expect(wrapper.text()).toContain('2 faktura(e) kasni')
    expect(wrapper.find('a').attributes('href')).toBe('/fakture?status=overdue')
  })
})
