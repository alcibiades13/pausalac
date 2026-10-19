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

export interface KpoMonthlySummaryRow {
  month: string
  products: string
  services: string
  total: string
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listKpoEntries(
  options: {
    dateFrom?: string
    dateTo?: string
    page?: number
    pageSize?: number
    search?: string
    ordering?: string
  } = {},
): Promise<Paginated<KPOEntry>> {
  return apiFetch<Paginated<KPOEntry>>('kpo/', {
    companyId: currentCompanyId(),
    params: {
      date_from: options.dateFrom,
      date_to: options.dateTo,
      page: options.page,
      page_size: options.pageSize,
      search: options.search,
      ordering: options.ordering,
    },
  })
}

export function getKpoMonthlySummary(year?: number): Promise<KpoMonthlySummaryRow[]> {
  return apiFetch<KpoMonthlySummaryRow[]>('kpo/monthly-summary/', {
    companyId: currentCompanyId(),
    params: { year },
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
