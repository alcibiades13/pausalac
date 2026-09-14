import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DocumentsView from '../DocumentsView.vue'
import { listDocuments, uploadDocument, deleteDocument, type AppDocument } from '@/services/documents'
import { listTaxResolutions } from '@/services/taxes'

vi.mock('@/services/documents', () => ({
  listDocuments: vi.fn<typeof listDocuments>(),
  uploadDocument: vi.fn<typeof uploadDocument>(),
  deleteDocument: vi.fn<typeof deleteDocument>(),
}))

vi.mock('@/services/taxes', () => ({
  listTaxResolutions: vi.fn<typeof listTaxResolutions>(),
}))

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
    uploaded_by_name: 'Marko Markovic',
    created_at: '2026-09-14T00:00:00Z',
    ...overrides,
  }
}

describe('DocumentsView', () => {
  beforeEach(() => {
    vi.mocked(listDocuments).mockReset()
    vi.mocked(uploadDocument).mockReset()
    vi.mocked(deleteDocument).mockReset()
    vi.mocked(listTaxResolutions).mockReset()
    vi.mocked(listTaxResolutions).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
  })

  it('shows an empty state when there are no documents', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(DocumentsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Još nema dokumenata.')
  })

  it('renders documents with category and metadata', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 1, next: null, previous: null, results: [doc()] })
    const wrapper = mount(DocumentsView)
    await flushPromises()
    expect(wrapper.text()).toContain('Ugovor sa klijentom')
    expect(wrapper.text()).toContain('Ugovor')
    expect(wrapper.text()).toContain('ugovor.pdf')
    expect(wrapper.text()).toContain('Marko Markovic')
  })

  it('reloads when the category filter changes', async () => {
    vi.mocked(listDocuments).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(DocumentsView)
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

    const wrapper = mount(DocumentsView)
    await flushPromises()

    const deleteButton = wrapper.findAll('button').find((b) => b.text() === 'Obriši')
    await deleteButton!.trigger('click')
    await flushPromises()

    expect(deleteDocument).toHaveBeenCalledWith(1)
    expect(listDocuments).toHaveBeenCalledTimes(2)
  })
})
