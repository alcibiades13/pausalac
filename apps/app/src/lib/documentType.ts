import type { InvoiceDocumentType } from '@/services/invoices'

export const DOCUMENT_TYPE_LABELS: Record<InvoiceDocumentType, string> = {
  invoice: 'Faktura',
  profaktura: 'Profaktura',
  avans: 'Avansni račun',
}
