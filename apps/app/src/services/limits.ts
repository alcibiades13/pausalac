import { apiFetch } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type WarningLevel = 'ok' | 'attention' | 'warning' | 'critical'

export interface LimitTrackerData {
  identifier: string
  period: { type: 'calendar_year' | 'trailing_12_months'; start: string; end: string }
  threshold: string
  current: string
  currency: string
  percentage: number
  remaining: string
  warning_level: WarningLevel
  projection: { estimated_period_end: string; label: 'procena' } | null
  approval_status: 'unverified' | 'confirmed'
}

export interface Limits {
  pausal_limit: LimitTrackerData
  vat_threshold: LimitTrackerData
}

export interface LimitsSimulation {
  before: Limits
  after: Limits
}

export interface LimitHistoryPoint {
  month: string
  cumulative: string
}

export interface LimitHistory {
  year: number
  threshold: string
  currency: string
  history: LimitHistoryPoint[]
  projection: LimitHistoryPoint[]
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function getLimits(): Promise<Limits> {
  return apiFetch<Limits>('limits/', { companyId: currentCompanyId() })
}

export function simulateLimits(amount: string): Promise<LimitsSimulation> {
  return apiFetch<LimitsSimulation>('limits/simulate/', {
    method: 'POST',
    companyId: currentCompanyId(),
    body: { amount },
  })
}

export function getLimitHistory(year?: number): Promise<LimitHistory> {
  return apiFetch<LimitHistory>('limits/pausal/history/', {
    companyId: currentCompanyId(),
    params: { year },
  })
}
