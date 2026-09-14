import type { InvoiceStatus } from '@/services/invoices'

export const STATUS_LABELS: Record<InvoiceStatus, string> = {
  draft: 'Nacrt',
  issued: 'Izdata',
  sent: 'Poslata',
  viewed: 'Viđena',
  partially_paid: 'Delimično plaćena',
  paid: 'Plaćena',
  overdue: 'Kasni',
  cancelled: 'Stornirana',
}

export const STATUS_VARIANTS: Record<InvoiceStatus, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  draft: 'neutral',
  issued: 'info',
  sent: 'info',
  viewed: 'info',
  partially_paid: 'warning',
  paid: 'success',
  overdue: 'danger',
  cancelled: 'neutral',
}

/**
 * Mirrors apps/invoices/services.py::TRANSITIONS on the backend — kept in
 * sync by hand (small, stable map) so the UI never offers a button the API
 * would reject with a 400. PARTIALLY_PAID/PAID have no entry on purpose —
 * voiding an invoice with money already against it needs a refund/
 * correction concept the master prompt explicitly defers (§96).
 */
const TRANSITIONS: Record<InvoiceStatus, InvoiceStatus[]> = {
  draft: ['issued', 'cancelled'],
  issued: ['cancelled', 'sent'],
  sent: ['cancelled'],
  viewed: [],
  partially_paid: [],
  paid: [],
  overdue: ['cancelled'],
  cancelled: [],
}

export function canTransitionTo(status: InvoiceStatus, target: InvoiceStatus): boolean {
  return TRANSITIONS[status].includes(target)
}

/**
 * Mirrors apps/invoices/services.py::PAYABLE_STATUSES — which statuses can
 * receive a recorded payment. Distinct from TRANSITIONS since the
 * resulting status (partially_paid vs. paid) is computed from the amount,
 * not a fixed target.
 */
export const PAYABLE_STATUSES: InvoiceStatus[] = ['issued', 'sent', 'partially_paid', 'overdue']

export function isPayable(status: InvoiceStatus): boolean {
  return PAYABLE_STATUSES.includes(status)
}
