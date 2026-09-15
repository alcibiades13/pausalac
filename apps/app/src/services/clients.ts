import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export interface Client {
  id: number
  client_type: 'individual' | 'company'
  name: string
  tax_id: string
  email: string
  phone: string
  address: string
  country: string
  default_currency: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ClientPayload = Pick<
  Client,
  'client_type' | 'name' | 'tax_id' | 'email' | 'phone' | 'address' | 'notes'
>

/** Master prompt §15/blueprint §6.3 client profile totals — GET /clients/{id}/summary/. */
export interface ClientSummary {
  total_invoiced: string
  total_paid: string
  outstanding: string
  invoice_count: number
  last_invoice_date: string | null
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listClients(
  options: { pageSize?: number; page?: number; search?: string } = {},
): Promise<Paginated<Client>> {
  return apiFetch<Paginated<Client>>('clients/', {
    companyId: currentCompanyId(),
    params: { page_size: options.pageSize, page: options.page, search: options.search },
  })
}

export function getClient(id: number | string): Promise<Client> {
  return apiFetch<Client>(`clients/${id}/`, { companyId: currentCompanyId() })
}

export function getClientSummary(id: number | string): Promise<ClientSummary> {
  return apiFetch<ClientSummary>(`clients/${id}/summary/`, { companyId: currentCompanyId() })
}

export function createClient(payload: Partial<ClientPayload>): Promise<Client> {
  return apiFetch<Client>('clients/', {
    method: 'POST',
    body: payload,
    companyId: currentCompanyId(),
  })
}

export function updateClient(id: number | string, payload: Partial<ClientPayload>): Promise<Client> {
  return apiFetch<Client>(`clients/${id}/`, {
    method: 'PATCH',
    body: payload,
    companyId: currentCompanyId(),
  })
}

export function deactivateClient(id: number | string): Promise<void> {
  return apiFetch(`clients/${id}/`, { method: 'DELETE', companyId: currentCompanyId() })
}
