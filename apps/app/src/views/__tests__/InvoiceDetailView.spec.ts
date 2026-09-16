import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import InvoiceDetailView from '../InvoiceDetailView.vue'
import { getInvoice, convertInvoice, duplicateInvoice, type Invoice } from '@/services/invoices'
import { listPayments } from '@/services/payments'
import { listDocuments, type AppDocument } from '@/services/documents'
import { i18n } from '@/i18n'

vi.mock('@/services/invoices', () => ({
  getInvoice: vi.fn<typeof getInvoice>(),
  issueInvoice: vi.fn<() => Promise<never>>(),
  cancelInvoice: vi.fn<() => Promise<never>>(),
  convertInvoice: vi.fn<typeof convertInvoice>(),
  duplicateInvoice: vi.fn<typeof duplicateInvoice>(),
  sendInvoice: vi.fn<() => Promise<never>>(),
  invoicePdfUrl: vi.fn<(id: number | string) => string>(
    (id) => `http://localhost/invoices/${id}/pdf/`,
  ),
}))

vi.mock('@/services/payments', () => ({
  listPayments: vi.fn<typeof listPayments>(),
  recordPayment: vi.fn<() => Promise<never>>(),
}))

vi.mock('@/services/documents', () => ({
  listDocuments: vi.fn<typeof listDocuments>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture/:id', name: 'invoice-detail', component: { template: '<div/>' }, props: true },
    { path: '/fakture/:id/izmeni', name: 'invoice-edit', component: { template: '<div/>' }, props: true },
    { path: '/klijenti/:id', name: 'client-detail', component: { template: '<div/>' }, props: true },
  ],
})

function baseInvoice(overrides: Partial<Invoice> = {}): Invoice {
  return {
    id: 1,
    client: 1,
    client_name: 'Klijent A',
    client_email: 'klijent@primer.rs',
    invoice_number: 'PRO-2026-001',
    status: 'issued',
    document_type: 'profaktura',
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
    issued_at: '2026-01-01T00:00:00Z',
    sent_at: null,
    paid_at: null,
    cancelled_at: null,
    created_at: '',
    updated_at: '',
    items: [],
    ...overrides,
  }
}

afterEach(() => {
  vi.restoreAllMocks()
})

async function mountDetail(invoice: Invoice, documents: AppDocument[] = []) {
  vi.mocked(getInvoice).mockResolvedValue(invoice)
  vi.mocked(listPayments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
  vi.mocked(listDocuments).mockResolvedValue({
    count: documents.length,
    next: null,
    previous: null,
    results: documents,
  })
  const wrapper = mount(InvoiceDetailView, {
    props: { id: String(invoice.id) },
    global: { plugins: [router, i18n] },
  })
  await flushPromises()
  return wrapper
}

describe('InvoiceDetailView document types', () => {
  beforeEach(() => {
    vi.mocked(getInvoice).mockReset()
    vi.mocked(listPayments).mockReset()
    vi.mocked(convertInvoice).mockReset()
    vi.mocked(duplicateInvoice).mockReset()
    vi.mocked(listDocuments).mockReset()
  })

  it('shows a "Konvertuj u fakturu" button for an issued, not-yet-converted profaktura', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'issued' }))
    expect(wrapper.text()).toContain('Konvertuj u fakturu')
  })

  it('hides the convert button once the profaktura has already been converted', async () => {
    const wrapper = await mountDetail(
      baseInvoice({ status: 'issued', converted_to: 2, converted_to_number: 'INV-2026-005' }),
    )
    expect(wrapper.text()).not.toContain('Konvertuj u fakturu')
    expect(wrapper.text()).toContain('INV-2026-005')
  })

  it('hides the convert button for a draft profaktura', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'draft' }))
    expect(wrapper.text()).not.toContain('Konvertuj u fakturu')
  })

  it('does not show the convert button for a regular invoice', async () => {
    const wrapper = await mountDetail(baseInvoice({ document_type: 'invoice', status: 'issued' }))
    expect(wrapper.text()).not.toContain('Konvertuj u fakturu')
  })

  it('hides "Evidentiraj uplatu" and the Uplate section for a profaktura', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'issued' }))
    expect(wrapper.text()).not.toContain('Evidentiraj uplatu')
    expect(wrapper.text()).not.toContain('Uplate')
  })

  it('shows "Evidentiraj uplatu" for a payable avans', async () => {
    const wrapper = await mountDetail(
      baseInvoice({ document_type: 'avans', status: 'issued' }),
    )
    expect(wrapper.text()).toContain('Evidentiraj uplatu')
  })

  it('converting navigates to the new invoice detail page', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'issued' }))
    vi.mocked(convertInvoice).mockResolvedValue(baseInvoice({ id: 2, document_type: 'invoice' }))

    const pushSpy = vi.spyOn(router, 'push')
    const buttons = wrapper.findAll('button')
    const convertButton = buttons.find((b) => b.text() === 'Konvertuj u fakturu')!
    await convertButton.trigger('click')
    await flushPromises()

    expect(convertInvoice).toHaveBeenCalledWith('1')
    expect(pushSpy).toHaveBeenCalledWith({ name: 'invoice-detail', params: { id: 2 } })
  })

  it('shows a provenance link when the invoice was converted from a profaktura', async () => {
    const wrapper = await mountDetail(
      baseInvoice({
        document_type: 'invoice',
        converted_from: 9,
        converted_from_number: 'PRO-2026-003',
      }),
    )
    expect(wrapper.text()).toContain('PRO-2026-003')
  })
})

describe('InvoiceDetailView duplication (master prompt §94)', () => {
  beforeEach(() => {
    vi.mocked(getInvoice).mockReset()
    vi.mocked(listPayments).mockReset()
    vi.mocked(duplicateInvoice).mockReset()
    vi.mocked(listDocuments).mockReset()
  })

  it('shows the "Dupliraj" button regardless of status', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'cancelled' }))
    expect(wrapper.text()).toContain('Dupliraj')
  })

  it('duplicates the invoice and navigates straight to the new draft\'s edit page', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'issued' }))
    vi.mocked(duplicateInvoice).mockResolvedValue(baseInvoice({ id: 5, status: 'draft' }))

    const pushSpy = vi.spyOn(router, 'push')
    const duplicateButton = wrapper.findAll('button').find((b) => b.text() === 'Dupliraj')!
    await duplicateButton.trigger('click')
    await flushPromises()

    expect(duplicateInvoice).toHaveBeenCalledWith('1')
    expect(pushSpy).toHaveBeenCalledWith({ name: 'invoice-edit', params: { id: 5 } })
  })

  it('shows an error message and does not navigate when duplication fails', async () => {
    const wrapper = await mountDetail(baseInvoice({ status: 'issued' }))
    vi.mocked(duplicateInvoice).mockRejectedValue(new Error('boom'))

    const routeBefore = router.currentRoute.value.fullPath
    const duplicateButton = wrapper.findAll('button').find((b) => b.text() === 'Dupliraj')!
    await duplicateButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Faktura nije mogla da se duplira.')
    expect(router.currentRoute.value.fullPath).toBe(routeBefore)
  })
})

describe('InvoiceDetailView documents section (master prompt §102)', () => {
  beforeEach(() => {
    vi.mocked(getInvoice).mockReset()
    vi.mocked(listPayments).mockReset()
    vi.mocked(listDocuments).mockReset()
  })

  function doc(overrides: Partial<AppDocument> = {}): AppDocument {
    return {
      id: 1,
      category: 'contract',
      title: 'Ugovor uz fakturu',
      description: '',
      file_url: 'http://minio.local/documents/1/file.pdf',
      original_filename: 'ugovor.pdf',
      content_type: 'application/pdf',
      size_bytes: 2048,
      tax_resolution: null,
      client: null,
      invoice: 1,
      payment: null,
      tax_obligation: null,
      uploaded_by_name: 'Marko Markovic',
      created_at: '2026-01-01T00:00:00Z',
      ...overrides,
    }
  }

  it('does not show a "Dokumenti" section when there are no linked documents', async () => {
    const wrapper = await mountDetail(baseInvoice())
    expect(wrapper.text()).not.toContain('Dokumenti')
  })

  it('lists documents linked to this invoice', async () => {
    const wrapper = await mountDetail(baseInvoice(), [doc()])

    expect(wrapper.text()).toContain('Dokumenti')
    expect(wrapper.text()).toContain('Ugovor uz fakturu')
    expect(listDocuments).toHaveBeenCalledWith(expect.objectContaining({ invoice: '1' }))
  })
})
