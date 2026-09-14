import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type ObligationStatus = 'pending' | 'paid' | 'overdue'

export interface TaxResolution {
  id: number
  effective_from: string
  effective_until: string
  tax_base: string
  income_tax_amount: string
  pio_amount: string
  health_amount: string
  unemployment_amount: string
  notes: string
  created_at: string
  rate_check_warnings: string[]
}

export interface TaxResolutionPayload {
  effective_from: string
  effective_until: string
  tax_base: string
  income_tax_amount: string
  pio_amount: string
  health_amount: string
  unemployment_amount: string
  notes?: string
}

export interface TaxObligation {
  id: number
  resolution: number
  period_start: string
  due_date: string
  income_tax_amount: string
  pio_amount: string
  health_amount: string
  unemployment_amount: string
  total_amount: string
  status: ObligationStatus
  paid_at: string | null
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function createTaxResolution(payload: TaxResolutionPayload): Promise<TaxResolution> {
  return apiFetch<TaxResolution>('taxes/resolutions/', {
    method: 'POST',
    body: payload,
    companyId: currentCompanyId(),
  })
}

export function listTaxResolutions(): Promise<Paginated<TaxResolution>> {
  return apiFetch<Paginated<TaxResolution>>('taxes/resolutions/', { companyId: currentCompanyId() })
}

export function listTaxObligations(
  options: { status?: ObligationStatus } = {},
): Promise<Paginated<TaxObligation>> {
  return apiFetch<Paginated<TaxObligation>>('taxes/obligations/', {
    companyId: currentCompanyId(),
    params: { status: options.status },
  })
}

export function markObligationPaid(id: number | string): Promise<TaxObligation> {
  return apiFetch<TaxObligation>(`taxes/obligations/${id}/mark-paid/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}
