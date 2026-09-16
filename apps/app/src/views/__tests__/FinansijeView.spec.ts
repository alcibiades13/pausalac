import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FinansijeView from '../FinansijeView.vue'
import { i18n } from '@/i18n'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/limiti', name: 'limits', component: { template: '<div/>' } },
    { path: '/kpo', name: 'kpo', component: { template: '<div/>' } },
    { path: '/obaveze', name: 'obligations', component: { template: '<div/>' } },
  ],
})

describe('FinansijeView', () => {
  it('links to Limiti, KPO and Obaveze', () => {
    const wrapper = mount(FinansijeView, { global: { plugins: [router, i18n] } })
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    expect(hrefs).toContain('/limiti')
    expect(hrefs).toContain('/kpo')
    expect(hrefs).toContain('/obaveze')
  })
})
