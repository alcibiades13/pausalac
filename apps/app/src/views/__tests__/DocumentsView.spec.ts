import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import DocumentsView from '../DocumentsView.vue'
import { listDocuments, uploadDocument, deleteDocument, type AppDocument } from '@/services/documents'
import { listTaxResolutions } from '@/services/taxes'
import { listClients, type Client } from '@/services/clients'
import { listInvoices, type Invoice } from '@/services/invoices'
import { i18n } from '@/i18n'

vi.mock('@/services/documents', () => ({
  listDocuments: vi.fn<typeof listDocuments>(),
  uploadDocument: vi.fn<typeof uploadDocument>(),
  deleteDocument: vi.fn<typeof deleteDocument>(),
}))

vi.mock('@/services/taxes', () => ({
  listTaxResolutions: vi.fn<typeof listTaxResolutions>(),
}))

vi.mock('@/services/clients', () => ({
  listClients: vi.fn<typeof listClients>(),
}))

vi.mock('@/services/invoices', () => ({
  listInvoices: vi.fn<typeof listInvoices>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/', component: { template: '<div />' } }],
})

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
    client: null,
    invoice: null,
    payment: null,
    tax_obligation: null,
    uploaded_by_name: 'Marko Markovic',
    created_at: '2026-09-14T00:00:00Z',
    ...overrides,
  }
}

function client(overrides: Partial<Client> = {}): Client {
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
    ...overrides,
  }
}

function invoice(overrides: Partial<Invoice> = {}): Invoice {
  return {
    id: 1,
    client: 1,
    client_name: 'Klijent A',
    client_email: '',
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

function mountView() {
  return mount(DocumentsView, { global: { plugins: [router, i18n] } })
}

describe('DocumentsView', () => {
  beforeEach(() => {
    vi.mocked(listDocuments).mockReset()
    vi.mocked(uploadDocument).mockReset()
    vi.mocked(deleteDocument).mockReset()
    vi.mocked(listTaxResolutions).mockReset()
    vi.mocked(listTaxResolutions).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listClients).mockReset()
    vi.mocked(listClients).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(listInvoices).mockReset()
    vi.mocked(listInvoices).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
  })

  it('shows an empty state when there are no documents', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Još nema dokumenata.')
  })

  it('renders documents with category and metadata', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 1, next: null, previous: null, results: [doc()] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Ugovor sa klijentom')
    expect(wrapper.text()).toContain('Ugovor')
    expect(wrapper.text()).toContain('ugovor.pdf')
    expect(wrapper.text()).toContain('Marko Markovic')
  })

  it('reloads when the category filter changes', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()

    const selects = wrapper.findAll('select')
    const categoryFilterSelect = selects[selects.length - 1]!
    await categoryFilterSelect.setValue('contract')
    await flushPromises()

    expect(listDocuments).toHaveBeenCalledWith(expect.objectContaining({ category: 'contract' }))
  })

  it('deletes a document and reloads the list', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 1, next: null, previous: null, results: [doc()] })
    vi.mocked(deleteDocument).mockResolvedValue(undefined)

    const wrapper = mountView()
    await flushPromises()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Obriši')
    await deleteButton!.trigger('click')
    await flushPromises()

    expect(deleteDocument).toHaveBeenCalledWith(1)
    expect(listDocuments).toHaveBeenCalledTimes(2)
  })

  describe('client/invoice link pickers (master prompt §102)', () => {
    it('uploads with the selected client and invoice linked', async () => {
      vi.mocked(listClients).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [client({ id: 3, name: 'Klijent C' })],
      })
      vi.mocked(listInvoices).mockResolvedValue({
        count: 1,
        next: null,
        previous: null,
        results: [invoice({ id: 4, invoice_number: 'INV-2026-004' })],
      })
      vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
      vi.mocked(uploadDocument).mockResolvedValue(doc())

      const wrapper = mountView()
      await flushPromises()

      const selects = wrapper.findAll('select')
      const clientSelect = selects[2]!
      const invoiceSelect = selects[3]!
      expect(clientSelect.text()).toContain('Klijent C')
      expect(invoiceSelect.text()).toContain('INV-2026-004')

      await wrapper.findAll('input[type="text"]')[0]!.setValue('Naslov')
      await clientSelect.setValue('3')
      await invoiceSelect.setValue('4')

      // Simulate picking a file, since jsdom won't let us assign FileList directly.
      const fileInput = wrapper.find<HTMLInputElement>('input#doc-file')
      const file = new File(['sadrzaj'], 'test.pdf', { type: 'application/pdf' })
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(uploadDocument).toHaveBeenCalledWith(
        expect.objectContaining({ client: 3, invoice: 4 }),
      )
    })

    it('uploads without a client/invoice link when left unset', async () => {
      vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
      vi.mocked(uploadDocument).mockResolvedValue(doc())

      const wrapper = mountView()
      await flushPromises()

      const fileInput = wrapper.find<HTMLInputElement>('input#doc-file')
      const file = new File(['sadrzaj'], 'test.pdf', { type: 'application/pdf' })
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')

      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(uploadDocument).toHaveBeenCalledWith(
        expect.objectContaining({ client: undefined, invoice: undefined }),
      )
    })
  })

  describe('?document= deep link (master prompt §115)', () => {
    it('highlights the matching row when a document query param is present', async () => {
      vi.mocked(listDocuments).mockResolvedValue({
        count: 2,
        next: null,
        previous: null,
        results: [doc({ id: 1 }), doc({ id: 2, title: 'Drugi dokument' })],
      })

      await router.push('/?document=2')
      const wrapper = mount(DocumentsView, { global: { plugins: [router, i18n] } })
      await flushPromises()

      const highlighted = wrapper.find('#document-2')
      const notHighlighted = wrapper.find('#document-1')
      expect(highlighted.classes()).toContain('ring-2')
      expect(notHighlighted.classes()).not.toContain('ring-2')
    })
  })
})
