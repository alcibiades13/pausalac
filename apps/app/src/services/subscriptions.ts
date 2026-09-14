import { apiFetch } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type SubscriptionStatus = 'trialing' | 'active' | 'grace_period' | 'cancelled' | 'expired'

export interface Plan {
  id: number
  identifier: string
  name: string
  price: string
  currency: string
  billing_interval: 'monthly'
  entitlements: Record<string, unknown>
}

export interface Subscription {
  id: number
  status: SubscriptionStatus
  plan: Plan | null
  trial_ends_at: string
  price_snapshot: string | null
  current_period_end: string | null
  cancelled_at: string | null
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listPlans(): Promise<Plan[]> {
  return apiFetch<Plan[]>('subscriptions/plans/')
}

export function getCurrentSubscription(): Promise<Subscription> {
  return apiFetch<Subscription>('subscriptions/current/', { companyId: currentCompanyId() })
}

export function activatePlan(planId: number): Promise<Subscription> {
  return apiFetch<Subscription>('subscriptions/activate/', {
    method: 'POST',
    body: { plan: planId },
    companyId: currentCompanyId(),
  })
}

export function cancelSubscription(): Promise<Subscription> {
  return apiFetch<Subscription>('subscriptions/cancel/', {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}
