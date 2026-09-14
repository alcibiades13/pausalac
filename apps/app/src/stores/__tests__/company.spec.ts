import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore, type Company, type Membership } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'

function membership(company: Partial<Company> & { id: number; name: string }): Membership {
  return {
    role: 'owner',
    status: 'active',
    company: {
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
      ...company,
    },
  }
}

describe('useCompanyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('is null when the user has no memberships', () => {
    const company = useCompanyStore()
    expect(company.currentCompany).toBeNull()
  })

  it('defaults to the first active membership', () => {
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      memberships: [membership({ id: 1, name: 'Firma A' }), membership({ id: 2, name: 'Firma B' })],
    }

    const company = useCompanyStore()
    expect(company.currentCompany?.name).toBe('Firma A')
    expect(company.currentCompanyId).toBe(1)
  })

  it('falls back to the first membership if a stale id is stored', () => {
    localStorage.setItem('pausalac.currentCompanyId', '999')
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      memberships: [membership({ id: 1, name: 'Firma A' })],
    }

    const company = useCompanyStore()
    expect(company.currentCompany?.name).toBe('Firma A')
  })

  it('lists every company the user has a membership in', () => {
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      memberships: [membership({ id: 1, name: 'Firma A' }), membership({ id: 2, name: 'Firma B' })],
    }

    const company = useCompanyStore()
    expect(company.companies.map((c) => c.name)).toEqual(['Firma A', 'Firma B'])
  })

  it('switches the active company via setCurrentCompany', () => {
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      memberships: [membership({ id: 1, name: 'Firma A' }), membership({ id: 2, name: 'Firma B' })],
    }

    const company = useCompanyStore()
    company.setCurrentCompany(2)
    expect(company.currentCompany?.name).toBe('Firma B')
    expect(company.currentCompanyId).toBe(2)
  })
})
