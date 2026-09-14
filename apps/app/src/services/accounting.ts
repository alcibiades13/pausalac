import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type GrantedRole = 'accountant' | 'accountant_admin'
export type ConnectionStatus = 'pending' | 'active' | 'declined' | 'revoked'
export type OrgStaffRole = 'admin' | 'staff'

export interface AccountingOrganization {
  id: number
  name: string
  contact_email: string
  pib: string | null
  created_at: string
  my_role: OrgStaffRole | null
}

export interface OrgStaffMembership {
  id: number
  user: number
  user_email: string
  organization: number
  role: OrgStaffRole
  status: 'active' | 'revoked'
  created_at: string
}

/** Org-side: which client companies this organization is connected to. */
export interface OrganizationConnection {
  id: number
  company: number
  company_name: string
  company_pib: string | null
  granted_role: GrantedRole
  status: ConnectionStatus
  created_at: string
  accepted_at: string | null
  revoked_at: string | null
}

/** Client-side ("Moj računovođa"): which organizations are connected to the current company. */
export interface ClientConnection {
  id: number
  organization: number
  organization_name: string
  granted_role: GrantedRole
  status: ConnectionStatus
  created_at: string
  accepted_at: string | null
  revoked_at: string | null
}

export type PortfolioStatus = 'ok' | 'attention' | 'critical'

/** `percentage`/`warning_level` are null only if no RegulatoryRule is
 * active for that identifier as of today — a data problem, not expected
 * in practice (apps/limits seeds these), but the API doesn't hide it. */
export interface PortfolioLimitTracker {
  percentage: number | null
  warning_level: 'ok' | 'attention' | 'warning' | 'critical' | null
}

/** One row of the accountant's client-portfolio table (master prompt §29). */
export interface ClientPortfolioRow {
  company_id: number
  company_name: string
  company_pib: string | null
  granted_role: GrantedRole
  status: PortfolioStatus
  revenue_ytd: string
  currency: string
  pausal_limit: PortfolioLimitTracker
  vat_threshold: PortfolioLimitTracker
  next_obligation_due: string | null
  next_obligation_overdue: boolean
  overdue_invoice_count: number
  missing_document_count: number
  /** Always null — no SEF/fiscalization integration exists yet (§29's
   * column reserved for when one does). */
  integration_errors: string | null
}

export interface PortfolioSummary {
  total: number
  ok: number
  attention: number
  critical: number
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listOrganizations(): Promise<Paginated<AccountingOrganization>> {
  return apiFetch<Paginated<AccountingOrganization>>('accounting/organizations/')
}

export function createOrganization(payload: {
  name: string
  contact_email?: string
  pib?: string
}): Promise<AccountingOrganization> {
  return apiFetch<AccountingOrganization>('accounting/organizations/', {
    method: 'POST',
    body: payload,
  })
}

export function listOrgStaff(organizationId: number): Promise<OrgStaffMembership[]> {
  return apiFetch<OrgStaffMembership[]>(`accounting/organizations/${organizationId}/staff/`)
}

export function addOrgStaff(
  organizationId: number,
  payload: { email: string; role: OrgStaffRole },
): Promise<OrgStaffMembership> {
  return apiFetch<OrgStaffMembership>(`accounting/organizations/${organizationId}/staff/`, {
    method: 'POST',
    body: payload,
  })
}

export function removeOrgStaff(organizationId: number, membershipId: number): Promise<void> {
  return apiFetch<void>(`accounting/organizations/${organizationId}/staff/${membershipId}/`, {
    method: 'DELETE',
  })
}

export function listOrgConnections(organizationId: number): Promise<OrganizationConnection[]> {
  return apiFetch<OrganizationConnection[]>(
    `accounting/organizations/${organizationId}/connections/`,
  )
}

export function createOrgConnection(
  organizationId: number,
  payload: { company_pib: string; granted_role: GrantedRole },
): Promise<OrganizationConnection> {
  return apiFetch<OrganizationConnection>(
    `accounting/organizations/${organizationId}/connections/`,
    { method: 'POST', body: payload },
  )
}

export function listClientConnections(): Promise<Paginated<ClientConnection>> {
  return apiFetch<Paginated<ClientConnection>>('accounting/connections/', {
    companyId: currentCompanyId(),
  })
}

export function acceptConnection(id: number): Promise<ClientConnection> {
  return apiFetch<ClientConnection>(`accounting/connections/${id}/accept/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}

export function declineConnection(id: number): Promise<ClientConnection> {
  return apiFetch<ClientConnection>(`accounting/connections/${id}/decline/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}

export function revokeConnection(id: number): Promise<ClientConnection> {
  return apiFetch<ClientConnection>(`accounting/connections/${id}/revoke/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}

export function getClientPortfolio(
  organizationId: number,
  options: {
    status?: PortfolioStatus
    search?: string
    ordering?: 'name' | '-name' | 'revenue' | '-revenue'
    page?: number
  } = {},
): Promise<Paginated<ClientPortfolioRow> & { summary: PortfolioSummary }> {
  return apiFetch<Paginated<ClientPortfolioRow> & { summary: PortfolioSummary }>(
    `accounting/organizations/${organizationId}/dashboard/`,
    { params: options },
  )
}
