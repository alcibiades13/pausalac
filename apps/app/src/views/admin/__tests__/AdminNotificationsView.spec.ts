import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminNotificationsView from '../AdminNotificationsView.vue'
import { listAdminNotifications } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminNotifications: vi.fn<typeof listAdminNotifications>(),
}))

describe('AdminNotificationsView', () => {
  beforeEach(() => {
    vi.mocked(listAdminNotifications).mockReset()
  })

  it('renders notifications returned by the service', async () => {
    vi.mocked(listAdminNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          recipient_email: 'vlasnik@pausalac.rs',
          event_type: 'invoice_overdue',
          priority: 'attention',
          channel: 'email',
          status: 'sent',
          read_at: null,
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminNotificationsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('vlasnik@pausalac.rs')
    expect(wrapper.text()).toContain('invoice_overdue')
  })
})
