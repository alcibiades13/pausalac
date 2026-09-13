import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type InvoiceStatus =
  | 'draft'
  | 'issued'
  | 'sent'
  | 'viewed'
  | 'partially_paid'
  | 'paid'
  | 'overdue'
  | 'cancelled'

export interface InvoiceLineItem {
  id?: number
  description: string
  quantity: string
  unit_price: string
  line_total?: string
  position?: number
}

export interface Invoice {
  id: number
  client: number
  client_name: string
  invoice_number: string | null
  status: InvoiceStatus
  issue_date: string
  due_date: string
  service_date: string
  currency: string
  total: string
  notes: string
  issued_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
  items: InvoiceLineItem[]
}

export interface InvoiceDraftPayload {
  client: number
  issue_date: string
  due_date: string
  service_date: string
  notes: string
  items: Pick<InvoiceLineItem, 'description' | 'quantity' | 'unit_price'>[]
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listInvoices(options: { status?: InvoiceStatus } = {}): Promise<Paginated<Invoice>> {
  return apiFetch<Paginated<Invoice>>('invoices/', {
    companyId: currentCompanyId(),
    params: { status: options.status },
  })
}

export function getInvoice(id: number | string): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/`, { companyId: currentCompanyId() })
}

export function createInvoice(payload: InvoiceDraftPayload): Promise<Invoice> {
  return apiFetch<Invoice>('invoices/', { method: 'POST', body: payload, companyId: currentCompanyId() })
}

export function updateInvoice(id: number | string, payload: InvoiceDraftPayload): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/`, {
    method: 'PATCH',
    body: payload,
    companyId: currentCompanyId(),
  })
}

export function issueInvoice(id: number | string): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/issue/`, { method: 'POST', companyId: currentCompanyId() })
}

export function cancelInvoice(id: number | string): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/cancel/`, { method: 'POST', companyId: currentCompanyId() })
}
