import { apiFetch } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'
import type { OnboardingStatus } from '@/services/companies'

export type BusinessHealthStatus = 'ok' | 'attention' | 'critical'

export interface AttentionItem {
  type: string
  message: string
  action: { route: string; query?: Record<string, string> }
}

export interface Dashboard {
  business_health: { status: BusinessHealthStatus; reasons: string[] }
  attention: AttentionItem[]
  revenue: { ytd: string; currency: string; basis: 'invoiced' }
  outstanding: {
    count: number
    total: string
    currency: string
    overdue_count: number
    overdue_total: string
  }
  onboarding: OnboardingStatus
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
