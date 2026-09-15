import { apiFetch, buildApiUrl, type Paginated } from '@/lib/api'
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

export type InvoiceDocumentType = 'invoice' | 'profaktura' | 'avans'

export type InvoiceLineItemType = 'service' | 'product'

export interface InvoiceLineItem {
  id?: number
  description: string
  item_type: InvoiceLineItemType
  quantity: string
  unit_price: string
  line_total?: string
  position?: number
}

export interface Invoice {
  id: number
  client: number
  client_name: string
  client_email: string
  invoice_number: string | null
  status: InvoiceStatus
  document_type: InvoiceDocumentType
  converted_from: number | null
  converted_from_number: string | null
  converted_to: number | null
  converted_to_number: string | null
  issue_date: string
  due_date: string
  service_date: string
  currency: string
  total: string
  notes: string
  issued_at: string | null
  sent_at: string | null
  paid_at: string | null
  cancelled_at: string | null
  created_at: string
  updated_at: string
  items: InvoiceLineItem[]
}

export interface InvoiceDraftPayload {
  client: number
  document_type?: InvoiceDocumentType
  issue_date: string
  due_date: string
  service_date: string
  notes: string
  items: Pick<InvoiceLineItem, 'description' | 'item_type' | 'quantity' | 'unit_price'>[]
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listInvoices(
  options: {
    status?: InvoiceStatus
    documentType?: InvoiceDocumentType
    client?: number | string
  } = {},
): Promise<Paginated<Invoice>> {
  return apiFetch<Paginated<Invoice>>('invoices/', {
    companyId: currentCompanyId(),
    params: {
      status: options.status,
      document_type: options.documentType,
      client: options.client,
    },
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

/**
 * Profaktura -> new draft Invoice (Phase 6c) — the resulting invoice is a
 * normal, independently editable draft; nothing about it stays linked to
 * the source profaktura other than the one-way `converted_from` field.
 */
export function convertInvoice(id: number | string): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/convert/`, { method: 'POST', companyId: currentCompanyId() })
}

/**
 * Master prompt §94: "When previous invoice exists: allow duplication."
 * Works from any status/document type — see InvoiceService.duplicate_invoice.
 */
export function duplicateInvoice(id: number | string): Promise<Invoice> {
  return apiFetch<Invoice>(`invoices/${id}/duplicate/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}

/**
 * A plain URL, not an apiFetch call — meant for `<a href>`/new-tab use.
 * The backend's `pdf` action deliberately doesn't require X-Company-Id
 * (apps/invoices/views.py) since a plain link navigation can't set one;
 * the session cookie alone is enough to authenticate it.
 */
export function invoicePdfUrl(id: number | string): string {
  return buildApiUrl(`invoices/${id}/pdf/`)
}

export function sendInvoice(
  id: number | string,
  payload: { recipientEmail?: string; message?: string } = {},
): Promise<{ detail: string }> {
  return apiFetch<{ detail: string }>(`invoices/${id}/send/`, {
    method: 'POST',
    body: { recipient_email: payload.recipientEmail, message: payload.message },
    companyId: currentCompanyId(),
  })
}
