import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type PaymentMethod = 'bank_transfer' | 'cash' | 'other'

export interface Payment {
  id: number
  invoice: number
  amount: string
  currency: string
  paid_at: string
  method: PaymentMethod
  notes: string
  created_at: string
}

export interface PaymentPayload {
  invoice: number
  amount: string
  paid_at: string
  method: PaymentMethod
  notes: string
  idempotency_key: string
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listPayments(options: { invoice: number | string }): Promise<Paginated<Payment>> {
  return apiFetch<Paginated<Payment>>('payments/', {
    companyId: currentCompanyId(),
    params: { invoice: options.invoice },
  })
}

export function recordPayment(payload: PaymentPayload): Promise<Payment> {
  return apiFetch<Payment>('payments/', { method: 'POST', body: payload, companyId: currentCompanyId() })
}
