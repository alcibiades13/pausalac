import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminDocumentsView from '../AdminDocumentsView.vue'
import { listAdminDocuments } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminDocuments: vi.fn<typeof listAdminDocuments>(),
}))

describe('AdminDocumentsView', () => {
  beforeEach(() => {
    vi.mocked(listAdminDocuments).mockReset()
  })

  it('renders documents returned by the service', async () => {
    vi.mocked(listAdminDocuments).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          category: 'contract',
          title: 'Ugovor',
          original_filename: 'ugovor.pdf',
          size_bytes: 1024,
          uploaded_by_email: 'vlasnik@pausalac.rs',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminDocumentsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('Ugovor')
    expect(wrapper.text()).toContain('vlasnik@pausalac.rs')
  })
})
