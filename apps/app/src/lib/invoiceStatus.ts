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
 * would reject with a 400. Only draft/issued/cancelled are reachable until
 * Phase 2d adds email/payments.
 */
const TRANSITIONS: Record<InvoiceStatus, InvoiceStatus[]> = {
  draft: ['issued', 'cancelled'],
  issued: ['cancelled'],
  sent: [],
  viewed: [],
  partially_paid: [],
  paid: [],
  overdue: [],
  cancelled: [],
}

export function canTransitionTo(status: InvoiceStatus, target: InvoiceStatus): boolean {
  return TRANSITIONS[status].includes(target)
}
