import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent } from 'vue'
import ClientFormView from '../ClientFormView.vue'
import { createClient, getClient, updateClient, type Client } from '@/services/clients'
import { ApiError } from '@/lib/api'

vi.mock('@/services/clients', () => ({
  createClient: vi.fn<typeof createClient>(),
  getClient: vi.fn<typeof getClient>(),
  updateClient: vi.fn<typeof updateClient>(),
}))

function baseClient(overrides: Partial<Client> = {}): Client {
  return {
    id: 1,
    client_type: 'company',
    name: 'Test Klijent DOO',
    tax_id: '123456789',
    email: 'klijent@primer.rs',
    phone: '',
    address: '',
    country: 'RS',
    default_currency: 'RSD',
    notes: '',
    is_active: true,
    created_at: '',
    updated_at: '',
    ...overrides,
  }
}

function buildRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div/>' } },
      { path: '/klijenti', name: 'clients', component: { template: '<div/>' } },
      { path: '/klijenti/novi', name: 'client-new', component: ClientFormView },
      {
        path: '/klijenti/:id',
        name: 'client-detail',
        component: { template: '<div>detail</div>' },
        props: true,
      },
      {
        path: '/klijenti/:id/izmeni',
        name: 'client-edit',
        component: ClientFormView,
        props: true,
      },
    ],
  })
}

describe('ClientFormView', () => {
  beforeEach(() => {
    vi.mocked(createClient).mockReset()
    vi.mocked(getClient).mockReset()
    vi.mocked(updateClient).mockReset()
  })

  describe('create mode', () => {
    it('submits the form and navigates to the new client detail page', async () => {
      vi.mocked(createClient).mockResolvedValue(baseClient({ id: 9 }))
      const router = buildRouter()
      await router.push('/klijenti/novi')
      await router.isReady()
      const wrapper = mount(ClientFormView, { global: { plugins: [router] } })
      await flushPromises()

      await wrapper.find('#client_type').setValue('company')
      const nameInput = wrapper.find('input')
      await nameInput.setValue('Novi klijent DOO')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(createClient).toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('client-detail')
      expect(router.currentRoute.value.params.id).toBe('9')
    })

    it('shows field errors from the API without navigating', async () => {
      vi.mocked(createClient).mockRejectedValue(
        new ApiError({
          code: 'VALIDATION_ERROR',
          message: 'Neispravni podaci.',
          request_id: '1',
          fields: { name: ['Naziv je obavezan.'] },
        }),
      )
      const router = buildRouter()
      await router.push('/klijenti/novi')
      await router.isReady()
      const wrapper = mount(ClientFormView, { global: { plugins: [router] } })
      await flushPromises()

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(wrapper.text()).toContain('Naziv je obavezan.')
      expect(router.currentRoute.value.name).toBe('client-new')
    })
  })

  describe('edit mode', () => {
    it('loads the existing client into the form', async () => {
      vi.mocked(getClient).mockResolvedValue(baseClient())
      const router = buildRouter()
      await router.push('/klijenti/1/izmeni')
      await router.isReady()
      const wrapper = mount(ClientFormView, { props: { id: '1' }, global: { plugins: [router] } })
      await flushPromises()

      const nameInput = wrapper.find<HTMLInputElement>('input')
      expect(nameInput.element.value).toBe('Test Klijent DOO')
    })

    it('updates the client and navigates to its detail page', async () => {
      vi.mocked(getClient).mockResolvedValue(baseClient())
      vi.mocked(updateClient).mockResolvedValue(baseClient({ name: 'Izmenjeno' }))
      const router = buildRouter()
      await router.push('/klijenti/1/izmeni')
      await router.isReady()
      const wrapper = mount(ClientFormView, { props: { id: '1' }, global: { plugins: [router] } })
      await flushPromises()

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(updateClient).toHaveBeenCalledWith('1', expect.any(Object))
      expect(router.currentRoute.value.name).toBe('client-detail')
    })
  })

  describe('unsaved-changes guard', () => {
    it('prompts before leaving a dirty form', async () => {
      vi.mocked(getClient).mockResolvedValue(baseClient())
      const router = buildRouter()
      await router.push('/klijenti/1/izmeni')
      await router.isReady()
      const RootComponent = defineComponent({ template: '<router-view />' })
      const wrapper = mount(RootComponent, { global: { plugins: [router] } })
      await flushPromises()

      const nameInput = wrapper.find<HTMLInputElement>('input')
      await nameInput.setValue('Izmenjeno bez čuvanja')

      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
      await router.push('/klijenti')
      await flushPromises()

      expect(confirmSpy).toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('client-edit')
      confirmSpy.mockRestore()
    })

    it('does not prompt when navigating away right after a successful save', async () => {
      vi.mocked(getClient).mockResolvedValue(baseClient())
      vi.mocked(updateClient).mockResolvedValue(baseClient({ name: 'Izmenjeno' }))
      const router = buildRouter()
      await router.push('/klijenti/1/izmeni')
      await router.isReady()
      const RootComponent = defineComponent({ template: '<router-view />' })
      const wrapper = mount(RootComponent, { global: { plugins: [router] } })
      await flushPromises()

      const confirmSpy = vi.spyOn(window, 'confirm')
      const nameInput = wrapper.find<HTMLInputElement>('input')
      await nameInput.setValue('Izmenjeno')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      // The save itself navigates away (to client-detail) — markClean() must
      // have run before that push, or the unsaved-changes guard would have
      // blocked its own component's save-and-navigate.
      expect(confirmSpy).not.toHaveBeenCalled()
      expect(router.currentRoute.value.name).toBe('client-detail')
      confirmSpy.mockRestore()
    })
  })
})
