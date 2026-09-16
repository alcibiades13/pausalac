import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminAuditLogView from '../AdminAuditLogView.vue'
import { listAdminAuditLog } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminAuditLog: vi.fn<typeof listAdminAuditLog>(),
}))

describe('AdminAuditLogView', () => {
  beforeEach(() => {
    vi.mocked(listAdminAuditLog).mockReset()
  })

  it('renders audit log entries returned by the service', async () => {
    vi.mocked(listAdminAuditLog).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          actor_email: 'super@pausalac.rs',
          entity_type: 'plan',
          entity_id: '1',
          action: 'admin_updated',
          old_value: null,
          new_value: null,
          source: 'api',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminAuditLogView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('super@pausalac.rs')
    expect(wrapper.text()).toContain('admin_updated')
  })

  it('shows "sistem" when no actor is attached to an entry', async () => {
    vi.mocked(listAdminAuditLog).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: null,
          company_name: null,
          actor_email: null,
          entity_type: 'user',
          entity_id: '1',
          action: 'signup_completed',
          old_value: null,
          new_value: null,
          source: 'api',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })
    const wrapper = mount(AdminAuditLogView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('sistem')
  })
})
