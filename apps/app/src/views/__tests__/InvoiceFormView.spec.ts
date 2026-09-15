import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import InvoiceFormView from '../InvoiceFormView.vue'
import { listClients, type Client } from '@/services/clients'
import { createInvoice, type Invoice } from '@/services/invoices'

vi.mock('@/services/clients', () => ({
  listClients: vi.fn<typeof listClients>(),
}))

vi.mock('@/services/invoices', () => ({
  createInvoice: vi.fn<typeof createInvoice>(),
  getInvoice: vi.fn<() => Promise<never>>(),
  updateInvoice: vi.fn<() => Promise<never>>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
    { path: '/fakture/:id', name: 'invoice-detail', component: { template: '<div/>' } },
    { path: '/klijenti/novi', name: 'client-new', component: { template: '<div/>' } },
  ],
})

function client(): Client {
  return {
    id: 1,
    client_type: 'company',
    name: 'Klijent A',
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
}

function invoiceResult(): Invoice {
  return {
    id: 1,
    client: 1,
    client_name: 'Klijent A',
    client_email: '',
    invoice_number: null,
    status: 'draft',
    document_type: 'invoice',
    converted_from: null,
    converted_from_number: null,
    converted_to: null,
    converted_to_number: null,
    issue_date: '2026-01-01',
    due_date: '2026-01-15',
    service_date: '2026-01-01',
    currency: 'RSD',
    total: '1000.00',
    notes: '',
    issued_at: null,
    sent_at: null,
    paid_at: null,
    cancelled_at: null,
    created_at: '',
    updated_at: '',
    items: [],
  }
}

describe('InvoiceFormView', () => {
  beforeEach(() => {
    vi.mocked(listClients).mockReset()
    vi.mocked(createInvoice).mockReset()
    vi.mocked(listClients).mockResolvedValue({ count: 1, next: null, previous: null, results: [client()] })
  })

  it('defaults the line item type to service and submits it with the payload', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router] } })
    await flushPromises()

    const select = wrapper.find('select[id]:not([id="client"])')
    expect((select.element as HTMLSelectElement).value).toBe('service')

    await wrapper.find('input[type="text"]').setValue('Konsalting')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [expect.objectContaining({ item_type: 'service', description: 'Konsalting' })],
      }),
    )
  })

  it('submits product when the type is changed', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router] } })
    await flushPromises()

    const select = wrapper.find('select[id]:not([id="client"])')
    await select.setValue('product')
    await wrapper.find('input[type="text"]').setValue('Widget')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [expect.objectContaining({ item_type: 'product', description: 'Widget' })],
      }),
    )
  })

  it('defaults to document_type invoice and the "Nova faktura" heading when no type prop is given', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Nova faktura')

    await wrapper.find('input[type="text"]').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(expect.objectContaining({ document_type: 'invoice' }))
  })

  it('shows the profaktura heading and sends document_type profaktura when created via that route', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, {
      props: { documentType: 'profaktura' },
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Nova profaktura')

    await wrapper.find('input[type="text"]').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({ document_type: 'profaktura' }),
    )
  })

  it('shows the avans heading and sends document_type avans when created via that route', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, {
      props: { documentType: 'avans' },
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Novi avans')

    await wrapper.find('input[type="text"]').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(expect.objectContaining({ document_type: 'avans' }))
  })
})
