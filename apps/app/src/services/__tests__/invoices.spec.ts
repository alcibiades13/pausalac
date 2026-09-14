import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore, type Membership } from '@/stores/auth'
import { invoicePdfUrl } from '@/services/invoices'

function membership(companyId: number): Membership {
  return {
    role: 'owner',
    status: 'active',
    company: {
      id: companyId,
      name: 'Firma',
      legal_name: '',
      pib: null,
      address: '',
      city: '',
      country: 'RS',
      activity_code: '',
      default_currency: 'RSD',
      bank_account: '',
      uses_sef: false,
      is_active: true,
      created_at: '',
      updated_at: '',
    },
  }
}

describe('invoicePdfUrl', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('builds a plain, fetch-free URL pointing at the pdf action', () => {
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      is_staff: false,
      memberships: [membership(1)],
    }

    const url = invoicePdfUrl(42)
    expect(url).toMatch(/\/api\/v1\/invoices\/42\/pdf\/$/)
    // No X-Company-Id-related query param leaks in — the backend action
    // resolves tenancy from the invoice itself, not this URL.
    expect(url).not.toContain('company')
  })
})
