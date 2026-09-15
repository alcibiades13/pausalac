import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ViseView from '../ViseView.vue'

const stub = { template: '<div/>' }
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: stub },
    { path: '/klijenti', name: 'clients', component: stub },
    { path: '/limiti', name: 'limits', component: stub },
    { path: '/kpo', name: 'kpo', component: stub },
    { path: '/obaveze', name: 'obligations', component: stub },
    { path: '/dokumenti', name: 'documents', component: stub },
    { path: '/racunovodja', name: 'accounting', component: stub },
    { path: '/pretplata', name: 'subscription', component: stub },
    { path: '/podesavanja', name: 'settings', component: stub },
    { path: '/obavestenja', name: 'notifications', component: stub },
    { path: '/prijava', name: 'login', component: stub },
  ],
})

describe('ViseView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('links to every remaining destination and offers a logout action', () => {
    const wrapper = mount(ViseView, { global: { plugins: [router] } })
    const hrefs = wrapper.findAll('a').map((a) => a.attributes('href'))
    expect(hrefs).toEqual([
      '/klijenti',
      '/limiti',
      '/kpo',
      '/obaveze',
      '/dokumenti',
      '/racunovodja',
      '/pretplata',
      '/podesavanja',
      '/obavestenja',
    ])
    expect(wrapper.text()).toContain('Odjavi se')
  })
})
