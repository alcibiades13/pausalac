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
    { path: '/klijenti/:id', name: 'client-detail', component: { template: '<div/>' } },
    { path: '/klijenti/:id/izmeni', name: 'client-edit', component: { template: '<div/>' } },
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

  it('links each client row to its detail page', async () => {
    vi.mocked(listClients).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 5,
          client_type: 'individual',
          name: 'Petar Petrović',
          tax_id: '',
          email: '',
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

    const link = wrapper.find('a[href="/klijenti/5"]')
    expect(link.exists()).toBe(true)
  })

  it('re-searches from page 1 when the search term changes', async () => {
    vi.mocked(listClients).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(ClientsListView, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('input').setValue('Petar')
    await flushPromises()

    expect(listClients).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 1, search: 'Petar' }),
    )
  })

  it('hides pagination controls when there is only one page', async () => {
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
          email: '',
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

    expect(wrapper.text()).not.toContain('Sledeća')
  })

  it('paginates forward and backward', async () => {
    const clientResult = {
      id: 1,
      client_type: 'company' as const,
      name: 'Test Klijent DOO',
      tax_id: '',
      email: '',
      phone: '',
      address: '',
      country: 'RS',
      default_currency: 'RSD',
      notes: '',
      is_active: true,
      created_at: '',
      updated_at: '',
    }
    vi.mocked(listClients).mockResolvedValue({
      count: 30,
      next: 'http://api/clients/?page=2',
      previous: null,
      results: [clientResult],
    })
    const wrapper = mount(ClientsListView, { global: { plugins: [router] } })
    await flushPromises()

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    expect(nextButton.attributes('disabled')).toBeUndefined()
    const prevButton = wrapper.findAll('button').find((b) => b.text() === 'Prethodna')!
    expect(prevButton.attributes('disabled')).toBeDefined()

    vi.mocked(listClients).mockResolvedValue({
      count: 30,
      next: null,
      previous: 'http://api/clients/?page=1',
      results: [clientResult],
    })
    await nextButton.trigger('click')
    await flushPromises()

    expect(listClients).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
