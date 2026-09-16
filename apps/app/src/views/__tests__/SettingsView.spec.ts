import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SettingsView from '../SettingsView.vue'
import { useAuthStore, type Membership } from '@/stores/auth'
import { updateCompany } from '@/services/companies'
import { i18n } from '@/i18n'

vi.mock('@/services/companies', () => ({
  updateCompany: vi.fn<typeof updateCompany>(),
}))

function membership(): Membership {
  return {
    role: 'owner',
    status: 'active',
    company: {
      id: 1,
      name: 'Firma A',
      legal_name: '',
      pib: '123456789',
      address: '',
      city: '',
      country: 'RS',
      activity_code: '',
      default_currency: 'RSD',
      bank_account: 'RS35...',
      uses_sef: false,
      is_active: true,
      created_at: '',
      updated_at: '',
    },
  }
}

describe('SettingsView', () => {
  beforeEach(() => {
    vi.mocked(updateCompany).mockReset()
  })

  it('pre-fills the form from the current company and saves changes', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.user = {
      id: 1,
      email: 'marko@pausalac.rs',
      first_name: '',
      last_name: '',
      is_email_verified: true,
      is_staff: false,
      language: 'sr',
      memberships: [membership()],
    }
    vi.mocked(updateCompany).mockResolvedValue(membership().company)
    // refreshMe() calls the real API — irrelevant to this test, and
    // otherwise fails in jsdom with no backend to talk to.
    auth.refreshMe = vi.fn<() => Promise<void>>().mockResolvedValue(undefined)

    const wrapper = mount(SettingsView, { global: { plugins: [pinia, i18n] } })
    const pibInput = wrapper.find('input[type="text"]')
    expect((pibInput.element as HTMLInputElement).value).toBe('123456789')

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(updateCompany).toHaveBeenCalledWith(1, { pib: '123456789', bank_account: 'RS35...' })
    expect(wrapper.text()).toContain('Sačuvano.')
  })
})
