import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ClientDetailView from '../ClientDetailView.vue'
import { getClient, getClientSummary, type Client, type ClientSummary } from '@/services/clients'
import { listInvoices, type Invoice } from '@/services/invoices'
import { listDocuments, type AppDocument } from '@/services/documents'
import { ApiError } from '@/lib/api'

vi.mock('@/services/clients', () => ({
  getClient: vi.fn<typeof getClient>(),
  getClientSummary: vi.fn<typeof getClientSummary>(),
}))

vi.mock('@/services/invoices', () => ({
  listInvoices: vi.fn<typeof listInvoices>(),
}))

vi.mock('@/services/documents', () => ({
  listDocuments: vi.fn<typeof listDocuments>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/klijenti/:id', name: 'client-detail', component: { template: '<div/>' }, props: true },
    { path: '/klijenti/:id/izmeni', name: 'client-edit', component: { template: '<div/>' }, props: true },
    { path: '/fakture/nova', name: 'invoice-new', component: { template: '<div/>' } },
    { path: '/fakture/:id', name: 'invoice-detail', component: { template: '<div/>' }, props: true },
  ],
})

function client(overrides: Partial<Client> = {}): Client {
  return {
    id: 1,
    client_type: 'company',
    name: 'Test Klijent DOO',
    tax_id: '123456789',
    email: 'klijent@primer.rs',
    phone: '+381 60 1234567',
    address: 'Knez Mihailova 1, Beograd',
    country: 'RS',
    default_currency: 'RSD',
    notes: '',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function summary(overrides: Partial<ClientSummary> = {}): ClientSummary {
  return {
    total_invoiced: '0.00',
    total_paid: '0.00',
    outstanding: '0.00',
    invoice_count: 0,
    last_invoice_date: null,
    ...overrides,
  }
}

function invoice(overrides: Partial<Invoice> = {}): Invoice {
  return {
    id: 1,
    client: 1,
    client_name: 'Test Klijent DOO',
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
    total: '1200.00',
    notes: '',
    issued_at: '2026-01-01T00:00:00Z',
    sent_at: null,
    paid_at: null,
    cancelled_at: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    items: [],
    ...overrides,
  }
}

function doc(overrides: Partial<AppDocument> = {}): AppDocument {
  return {
    id: 1,
    category: 'contract',
    title: 'Ugovor sa klijentom',
    description: '',
    file_url: 'http://minio.local/documents/1/file.pdf',
    original_filename: 'ugovor.pdf',
    content_type: 'application/pdf',
    size_bytes: 2048,
    tax_resolution: null,
    client: 1,
    invoice: null,
    payment: null,
    tax_obligation: null,
    uploaded_by_name: 'Marko Markovic',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

async function mountDetail(id = '1') {
  const wrapper = mount(ClientDetailView, {
    props: { id },
    global: { plugins: [router] },
  })
  await flushPromises()
  return wrapper
}

describe('ClientDetailView', () => {
  beforeEach(() => {
    vi.mocked(getClient).mockReset()
    vi.mocked(getClientSummary).mockReset()
    vi.mocked(listInvoices).mockReset()
    vi.mocked(listDocuments).mockReset()
  })

  it('renders contact info and summary totals once loaded', async () => {
    vi.mocked(getClient).mockResolvedValue(client())
    vi.mocked(getClientSummary).mockResolvedValue(
      summary({
        total_invoiced: '3600.00',
        total_paid: '1200.00',
        outstanding: '2400.00',
        invoice_count: 3,
        last_invoice_date: '2026-03-01',
      }),
    )
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    const wrapper = await mountDetail()

    expect(wrapper.text()).toContain('Test Klijent DOO')
    expect(wrapper.text()).toContain('123456789')
    expect(wrapper.text()).toContain('klijent@primer.rs')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('1. 3. 2026.')
  })

  it('requests invoices and documents scoped to this client', async () => {
    vi.mocked(getClient).mockResolvedValue(client())
    vi.mocked(getClientSummary).mockResolvedValue(summary())
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    await mountDetail('42')

    expect(listInvoices).toHaveBeenCalledWith(expect.objectContaining({ client: '42' }))
    expect(listDocuments).toHaveBeenCalledWith(expect.objectContaining({ client: '42' }))
  })

  it('shows an empty state for invoice history when the client has none', async () => {
    vi.mocked(getClient).mockResolvedValue(client())
    vi.mocked(getClientSummary).mockResolvedValue(summary())
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    const wrapper = await mountDetail()

    expect(wrapper.text()).toContain('Još nema faktura za ovog klijenta.')
  })

  it('lists invoice history with status and amount', async () => {
    vi.mocked(getClient).mockResolvedValue(client())
    vi.mocked(getClientSummary).mockResolvedValue(summary({ invoice_count: 1 }))
    vi.mocked(listInvoices).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [invoice()],
    })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    const wrapper = await mountDetail()

    expect(wrapper.text()).toContain('INV-2026-001')
    expect(wrapper.text()).toContain('1.200,00 RSD')
  })

  it('lists linked documents when present', async () => {
    vi.mocked(getClient).mockResolvedValue(client())
    vi.mocked(getClientSummary).mockResolvedValue(summary())
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [doc()],
    })

    const wrapper = await mountDetail()

    expect(wrapper.text()).toContain('Ugovor sa klijentom')
    expect(wrapper.text()).toContain('ugovor.pdf')
  })

  it('links "Nova faktura" to invoice-new pre-selecting this client', async () => {
    vi.mocked(getClient).mockResolvedValue(client({ id: 7 }))
    vi.mocked(getClientSummary).mockResolvedValue(summary())
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    const wrapper = await mountDetail('7')

    const newInvoiceLink = wrapper.findAll('a').find((a) => a.text().includes('Nova faktura'))
    expect(newInvoiceLink).toBeTruthy()
    expect(newInvoiceLink!.attributes('href')).toBe('/fakture/nova?client=7')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(getClient).mockRejectedValue(
      new ApiError({ code: 'SERVER_ERROR', message: 'Ne možemo trenutno.', request_id: '1' }),
    )
    vi.mocked(getClientSummary).mockResolvedValue(summary())
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })

    const wrapper = await mountDetail()

    expect(wrapper.text()).toContain('Ne možemo trenutno.')
  })
})
