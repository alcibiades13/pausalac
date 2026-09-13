import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '../App.vue'
import router from '../router'

describe('App', () => {
  it('redirects an unauthenticated visitor from the home route to login', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('network disabled in tests'))),
    )

    await router.push('/pocetna')
    await router.isReady()

    const wrapper = mount(App, { global: { plugins: [pinia, router] } })
    await vi.waitFor(() => expect(router.currentRoute.value.name).toBe('login'))

    expect(wrapper.text()).toContain('Prijava')
  })
})
