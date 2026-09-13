import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ClientsListView from '../ClientsListView.vue'
import { listClients } from '@/services/clients'
import { ApiError } from '@/lib/api'

vi.mock('@/services/clients', () => ({
  listClients: vi.fn<typeof listClients>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/klijenti/novi', name: 'client-new', component: { template: '<div/>' } },
    { path: '/klijenti/:id', name: 'client-edit', component: { template: '<div/>' } },
  ],
})

describe('ClientsListView', () => {
  beforeEach(() => {
    vi.mocked(listClients).mockReset()
  })

  it('shows an empty state when there are no clients', async () => {
    vi.mocked(listClients).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(ClientsListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Još nemaš klijente.')
  })

  it('renders the client list once loaded', async () => {
    vi.mocked(listClients).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          client_type: 'company',
          name: 'Test Klijent DOO',
          tax_id: '',
          email: 'klijent@primer.rs',
          phone: '',
          address: '',
          country: 'RS',
          default_currency: 'RSD',
          notes: '',
          is_active: true,
          created_at: '',
          updated_at: '',
        },
      ],
    })
    const wrapper = mount(ClientsListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Test Klijent DOO')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(listClients).mockRejectedValue(
      new ApiError({ code: 'SERVER_ERROR', message: 'Ne možemo trenutno.', request_id: '1' }),
    )
    const wrapper = mount(ClientsListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno.')
  })
})
