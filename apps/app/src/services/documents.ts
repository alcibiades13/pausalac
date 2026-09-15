import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type DocumentCategory =
  | 'tax_resolution'
  | 'contract'
  | 'sef_document'
  | 'fiscal_receipt'
  | 'other'

export interface AppDocument {
  id: number
  category: DocumentCategory
  title: string
  description: string
  file_url: string | null
  original_filename: string
  content_type: string
  size_bytes: number
  tax_resolution: number | null
  client: number | null
  invoice: number | null
  payment: number | null
  tax_obligation: number | null
  uploaded_by_name: string
  created_at: string
}

export interface DocumentUploadPayload {
  category: DocumentCategory
  title: string
  description?: string
  tax_resolution?: number
  client?: number
  invoice?: number
  file: File
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listDocuments(
  options: {
    category?: DocumentCategory
    taxResolution?: number
    client?: number | string
    invoice?: number | string
    search?: string
  } = {},
): Promise<Paginated<AppDocument>> {
  return apiFetch<Paginated<AppDocument>>('documents/', {
    companyId: currentCompanyId(),
    params: {
      category: options.category,
      tax_resolution: options.taxResolution,
      client: options.client,
      invoice: options.invoice,
      search: options.search,
    },
  })
}

export function uploadDocument(payload: DocumentUploadPayload): Promise<AppDocument> {
  const formData = new FormData()
  formData.set('category', payload.category)
  formData.set('title', payload.title)
  formData.set('description', payload.description ?? '')
  if (payload.tax_resolution !== undefined) {
    formData.set('tax_resolution', String(payload.tax_resolution))
  }
  if (payload.client !== undefined) {
    formData.set('client', String(payload.client))
  }
  if (payload.invoice !== undefined) {
    formData.set('invoice', String(payload.invoice))
  }
  formData.set('file', payload.file)

  return apiFetch<AppDocument>('documents/', {
    method: 'POST',
    body: formData,
    companyId: currentCompanyId(),
  })
}

export function deleteDocument(id: number | string): Promise<void> {
  return apiFetch<void>(`documents/${id}/`, { method: 'DELETE', companyId: currentCompanyId() })
}
