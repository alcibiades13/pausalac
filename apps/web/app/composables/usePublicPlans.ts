export interface PublicPlan {
  id: number
  identifier: string
  name: string
  price: string
  currency: string
  billing_interval: string
  entitlements: Record<string, unknown>
}

/**
 * Real, current pricing straight from apps.subscriptions.Plan (the same
 * rows the app itself reads at /pretplata) — GET /subscriptions/public/plans/,
 * deliberately unauthenticated (apps/api/apps/subscriptions/views.py).
 * Never hardcode these numbers as marketing copy: they'd drift from the
 * real Plan rows the moment pricing changes.
 */
export function usePublicPlans() {
  const config = useRuntimeConfig()
  return useFetch<PublicPlan[]>(`${config.public.apiBase}/v1/subscriptions/public/plans/`, {
    key: 'public-plans',
  })
}
