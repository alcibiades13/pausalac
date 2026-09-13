import { apiFetch } from '@/lib/api'
import type { Company } from '@/stores/auth'

export interface OnboardingStatus {
  completed: string[]
  missing: string[]
  percentage: number
}

export function createCompany(name: string): Promise<Company> {
  return apiFetch<Company>('companies/', { method: 'POST', body: { name } })
}

export function updateCompany(id: number, payload: Partial<Company>): Promise<Company> {
  return apiFetch<Company>(`companies/${id}/`, { method: 'PATCH', body: payload })
}

export function getOnboardingStatus(id: number): Promise<OnboardingStatus> {
  return apiFetch<OnboardingStatus>(`companies/${id}/onboarding/`)
}
