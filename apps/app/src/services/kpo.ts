import { apiFetch, buildApiUrl, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export interface KPOEntry {
  id: number
  sequence_number: number
  entry_date: string
  description: string
  product_revenue: string
  service_revenue: string
  total_revenue: string
  entry_type: 'original' | 'storno'
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listKpoEntries(
  options: { dateFrom?: string; dateTo?: string } = {},
): Promise<Paginated<KPOEntry>> {
  return apiFetch<Paginated<KPOEntry>>('kpo/', {
    companyId: currentCompanyId(),
    params: { date_from: options.dateFrom, date_to: options.dateTo },
  })
}

/**
 * Plain URLs, not apiFetch calls — for `<a href>` use. Own-id addressed
 * (company id in the path, not X-Company-Id) since a plain link download
 * can't set a custom header — same reasoning as invoicePdfUrl.
 */
export function kpoExportPdfUrl(): string {
  return buildApiUrl(`kpo/${currentCompanyId()}/export/pdf/`)
}

export function kpoExportXlsxUrl(): string {
  return buildApiUrl(`kpo/${currentCompanyId()}/export/xlsx/`)
}
