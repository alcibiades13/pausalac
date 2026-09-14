/**
 * In-app admin panel (master prompt §67, Phase 6b) — thin wrappers over
 * /api/v1/admin/*. Every list here is genuinely cross-tenant on the
 * backend (no X-Company-Id is ever sent), and every write action is
 * superuser-gated server-side — this module is a UI convenience only,
 * never the real access-control boundary (see apps/admin_panel/permissions.py).
 */
import { apiFetch, type Paginated } from '@/lib/api'
import type { Plan } from './subscriptions'
import type { InvoiceStatus } from './invoices'

export interface AdminUser {
  id: number
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  email_verified_at: string | null
}

export interface AdminCompany {
  id: number
  name: string
  legal_name: string
  pib: string | null
  city: string
  country: string
  is_active: boolean
  created_at: string
}

export interface AdminMembership {
  user_email: string
  role: 'owner' | 'accountant' | 'accountant_admin'
  status: 'active' | 'invited' | 'revoked'
}

export interface AdminSubscription {
  id: number
  company_id: number
  company_name: string
  status: 'trialing' | 'active' | 'grace_period' | 'cancelled' | 'expired'
  plan: Plan | null
  trial_ends_at: string
  price_snapshot: string | null
  current_period_end: string | null
  cancelled_at: string | null
}

export interface AdminInvoice {
  id: number
  company_id: number
  company_name: string
  client_name: string
  invoice_number: string | null
  status: InvoiceStatus
  issue_date: string
  due_date: string
  total: string
  currency: string
  created_at: string
}

export interface AdminDocument {
  id: number
  company_id: number
  company_name: string
  category: string
  title: string
  original_filename: string
  size_bytes: number
  uploaded_by_email: string | null
  created_at: string
}

export interface AdminTaxObligation {
  id: number
  company_id: number
  company_name: string
  period_start: string
  due_date: string
  total_amount: string
  status: string
  paid_at: string | null
}

export interface AdminRegulatoryRule {
  id: number
  identifier: string
  config: Record<string, unknown>
  effective_from: string
  effective_until: string | null
  source: string
  version: number
  approval_status: 'unverified' | 'confirmed'
  notes: string
  created_at: string
}

export interface AdminNotification {
  id: number
  company_id: number
  company_name: string
  recipient_email: string
  event_type: string
  priority: string
  channel: string
  status: string
  read_at: string | null
  created_at: string
}

export interface AdminAuditLogEntry {
  id: number
  company_id: number | null
  company_name: string | null
  actor_email: string | null
  entity_type: string
  entity_id: string
  action: string
  old_value: Record<string, unknown> | null
  new_value: Record<string, unknown> | null
  source: string
  created_at: string
}

export interface AdminIntegrationsStatus {
  sentry: { configured: boolean }
  storage: { configured: boolean }
  email: { configured: boolean }
  sef: { configured: boolean; note: string }
  checked_at: string
}

export interface ListParams {
  page?: number
  search?: string
  [key: string]: string | number | boolean | undefined
}

export function listAdminUsers(params: ListParams = {}) {
  return apiFetch<Paginated<AdminUser>>('admin/users/', { params })
}
export function deactivateAdminUser(id: number) {
  return apiFetch<AdminUser>(`admin/users/${id}/deactivate/`, { method: 'POST' })
}
export function reactivateAdminUser(id: number) {
  return apiFetch<AdminUser>(`admin/users/${id}/reactivate/`, { method: 'POST' })
}

export function listAdminCompanies(params: ListParams = {}) {
  return apiFetch<Paginated<AdminCompany>>('admin/companies/', { params })
}
export function listAdminCompanyMembers(companyId: number) {
  return apiFetch<AdminMembership[]>(`admin/companies/${companyId}/members/`)
}

export function listAdminSubscriptions(params: ListParams = {}) {
  return apiFetch<Paginated<AdminSubscription>>('admin/subscriptions/', { params })
}

export function listAdminPlans(params: ListParams = {}) {
  return apiFetch<Paginated<Plan & { is_active: boolean }>>('admin/plans/', { params })
}
export function createAdminPlan(payload: {
  identifier: string
  name: string
  price: string
  currency: string
  billing_interval: 'monthly'
  entitlements: Record<string, unknown>
  is_active: boolean
}) {
  return apiFetch('admin/plans/', { method: 'POST', body: payload })
}
export function updateAdminPlan(id: number, payload: Partial<Parameters<typeof createAdminPlan>[0]>) {
  return apiFetch(`admin/plans/${id}/`, { method: 'PATCH', body: payload })
}

export function listAdminInvoices(params: ListParams = {}) {
  return apiFetch<Paginated<AdminInvoice>>('admin/invoices/', { params })
}

export function listAdminDocuments(params: ListParams = {}) {
  return apiFetch<Paginated<AdminDocument>>('admin/documents/', { params })
}

export function listAdminTaxObligations(params: ListParams = {}) {
  return apiFetch<Paginated<AdminTaxObligation>>('admin/tax-obligations/', { params })
}

export function listAdminRegulatoryRules(params: ListParams = {}) {
  return apiFetch<Paginated<AdminRegulatoryRule>>('admin/rules/', { params })
}
export function createAdminRegulatoryRule(payload: {
  identifier: string
  config: Record<string, unknown>
  effective_from: string
  effective_until?: string | null
  source: string
  version: number
  notes?: string
}) {
  return apiFetch<AdminRegulatoryRule>('admin/rules/', { method: 'POST', body: payload })
}
export function approveAdminRegulatoryRule(id: number) {
  return apiFetch<AdminRegulatoryRule>(`admin/rules/${id}/approve/`, { method: 'POST' })
}

export function listAdminNotifications(params: ListParams = {}) {
  return apiFetch<Paginated<AdminNotification>>('admin/notifications/', { params })
}

export function listAdminAuditLog(params: ListParams = {}) {
  return apiFetch<Paginated<AdminAuditLogEntry>>('admin/audit-log/', { params })
}

export function getAdminIntegrationsStatus() {
  return apiFetch<AdminIntegrationsStatus>('admin/integrations/')
}
