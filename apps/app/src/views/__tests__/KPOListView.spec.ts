import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import KPOListView from '../KPOListView.vue'
import { listKpoEntries, type KPOEntry } from '@/services/kpo'
import { i18n } from '@/i18n'

vi.mock('@/services/kpo', () => ({
  listKpoEntries: vi.fn<typeof listKpoEntries>(),
  kpoExportPdfUrl: vi.fn<() => string>(() => 'http://localhost:8000/api/v1/kpo/1/export/pdf/'),
  kpoExportXlsxUrl: vi.fn<() => string>(() => 'http://localhost:8000/api/v1/kpo/1/export/xlsx/'),
}))

function entry(overrides: Partial<KPOEntry> = {}): KPOEntry {
  return {
    id: 1,
    sequence_number: 1,
    entry_date: '2026-09-14',
    description: 'Faktura INV-2026-001 — Klijent A',
    product_revenue: '300.00',
    service_revenue: '700.00',
    total_revenue: '1000.00',
    entry_type: 'original',
    ...overrides,
  }
}

function mountView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(KPOListView, { global: { plugins: [pinia, i18n] } })
}

describe('KPOListView', () => {
  beforeEach(() => {
    vi.mocked(listKpoEntries).mockReset()
  })

  it('shows an empty state when there are no entries', async () => {
    vi.mocked(listKpoEntries).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Još nema KPO stavki.')
  })

  it('renders entries with totals and a storno badge', async () => {
    vi.mocked(listKpoEntries).mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [entry(), entry({ id: 2, sequence_number: 2, entry_type: 'storno', description: 'Storno: Faktura INV-2026-001' })],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Faktura INV-2026-001')
    expect(wrapper.text()).toContain('Storno')
    expect(wrapper.text()).toContain('700,00 RSD')
    expect(wrapper.text()).toContain('1.000,00 RSD')
  })

  it('reloads when the date filters change', async () => {
    vi.mocked(listKpoEntries).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('input[type="date"]').setValue('2026-01-01')
    await flushPromises()

    expect(listKpoEntries).toHaveBeenCalledWith(expect.objectContaining({ dateFrom: '2026-01-01' }))
  })

  it('renders export links', async () => {
    vi.mocked(listKpoEntries).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    const links = wrapper.findAll('a')
    expect(links.some((a) => a.attributes('href')?.includes('export/pdf'))).toBe(true)
    expect(links.some((a) => a.attributes('href')?.includes('export/xlsx'))).toBe(true)
  })
})
