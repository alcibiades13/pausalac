import { apiFetch } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'
import type { OnboardingStatus } from '@/services/companies'
import type { Limits } from '@/services/limits'
import type { ObligationStatus } from '@/services/taxes'

export type BusinessHealthStatus = 'ok' | 'attention' | 'critical'

export interface AttentionItem {
  type: string
  message: string
  action: { route: string; query?: Record<string, string> }
}

export interface MonthlyRevenuePoint {
  month: string
  amount: string
}

export interface Dashboard {
  business_health: { status: BusinessHealthStatus; reasons: string[] }
  attention: AttentionItem[]
  revenue: { ytd: string; currency: string; basis: 'invoiced'; monthly_series: MonthlyRevenuePoint[] }
  outstanding: {
    count: number
    total: string
    currency: string
    overdue_count: number
    overdue_total: string
    paid_ytd: string
  }
  onboarding: OnboardingStatus
  limits: Limits
  next_obligation: {
    period_start: string
    due_date: string
    total_amount: string
    currency: string
    status: ObligationStatus
  } | null
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function getDashboard(): Promise<Dashboard> {
  return apiFetch<Dashboard>('analytics/dashboard/', { companyId: currentCompanyId() })
}
