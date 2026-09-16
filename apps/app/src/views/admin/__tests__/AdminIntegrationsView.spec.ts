import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminIntegrationsView from '../AdminIntegrationsView.vue'
import { getAdminIntegrationsStatus } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  getAdminIntegrationsStatus: vi.fn<typeof getAdminIntegrationsStatus>(),
}))

describe('AdminIntegrationsView', () => {
  beforeEach(() => {
    vi.mocked(getAdminIntegrationsStatus).mockReset()
  })

  it('reflects an unset Sentry DSN as not configured', async () => {
    vi.mocked(getAdminIntegrationsStatus).mockResolvedValue({
      sentry: { configured: false },
      storage: { configured: true },
      email: { configured: true },
      sef: { configured: false, note: 'No provider chosen yet (§39).' },
      checked_at: '2026-01-01T00:00:00Z',
    })
    const wrapper = mount(AdminIntegrationsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Nije podešeno')
    expect(wrapper.text()).toContain('No provider chosen yet')
  })

  it('reflects a configured Sentry DSN', async () => {
    vi.mocked(getAdminIntegrationsStatus).mockResolvedValue({
      sentry: { configured: true },
      storage: { configured: true },
      email: { configured: true },
      sef: { configured: false, note: 'No provider chosen yet (§39).' },
      checked_at: '2026-01-01T00:00:00Z',
    })
    const wrapper = mount(AdminIntegrationsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Podešeno')
  })
})
