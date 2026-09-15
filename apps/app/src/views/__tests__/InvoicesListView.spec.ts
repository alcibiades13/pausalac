import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import InvoicesListView from '../InvoicesListView.vue'
import { listInvoices } from '@/services/invoices'
import { ApiError } from '@/lib/api'

vi.mock('@/services/invoices', () => ({
  listInvoices: vi.fn<typeof listInvoices>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture/nova', name: 'invoice-new', component: { template: '<div/>' } },
    {
      path: '/fakture/nova/profaktura',
      name: 'invoice-new-profaktura',
      component: { template: '<div/>' },
    },
    { path: '/fakture/nova/avans', name: 'invoice-new-avans', component: { template: '<div/>' } },
    { path: '/fakture/:id', name: 'invoice-detail', component: { template: '<div/>' } },
  ],
})

describe('InvoicesListView', () => {
  beforeEach(() => {
    vi.mocked(listInvoices).mockReset()
  })

  it('shows an empty state when there are no invoices', async () => {
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(InvoicesListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Još nemaš fakture.')
  })

  it('renders the invoice list once loaded, with status and total', async () => {
    vi.mocked(listInvoices).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          client: 1,
          client_name: 'Test Klijent',
          client_email: 'klijent@primer.rs',
          invoice_number: 'INV-2026-001',
          status: 'issued',
          document_type: 'invoice',
          converted_from: null,
          converted_from_number: null,
          converted_to: null,
          converted_to_number: null,
          issue_date: '2026-01-01',
          due_date: '2026-01-15',
          service_date: '2026-01-01',
          currency: 'RSD',
          total: '7500.00',
          notes: '',
          issued_at: '2026-01-01T00:00:00Z',
          sent_at: null,
          paid_at: null,
          cancelled_at: null,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
          items: [],
        },
      ],
    })
    const wrapper = mount(InvoicesListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('INV-2026-001')
    expect(wrapper.text()).toContain('Test Klijent')
    expect(wrapper.text()).toContain('Izdata')
    expect(wrapper.text()).toContain('7.500,00 RSD')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(listInvoices).mockRejectedValue(
      new ApiError({ code: 'SERVER_ERROR', message: 'Ne možemo trenutno.', request_id: '1' }),
    )
    const wrapper = mount(InvoicesListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno.')
  })

  it('offers three explicit create buttons for the three document types', async () => {
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(InvoicesListView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('+ Faktura')
    expect(wrapper.text()).toContain('+ Profaktura')
    expect(wrapper.text()).toContain('+ Avans')
  })

  it('re-fetches with the selected document type when the type filter changes', async () => {
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(InvoicesListView, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.find('#document-type-filter').setValue('profaktura')
    await flushPromises()

    expect(listInvoices).toHaveBeenLastCalledWith(
      expect.objectContaining({ documentType: 'profaktura' }),
    )
  })
})
