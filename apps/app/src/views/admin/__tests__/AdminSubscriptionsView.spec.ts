import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminSubscriptionsView from '../AdminSubscriptionsView.vue'
import { listAdminSubscriptions } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminSubscriptions: vi.fn<typeof listAdminSubscriptions>(),
}))

describe('AdminSubscriptionsView', () => {
  beforeEach(() => {
    vi.mocked(listAdminSubscriptions).mockReset()
  })

  it('renders subscriptions returned by the service', async () => {
    vi.mocked(listAdminSubscriptions).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          status: 'trialing',
          plan: null,
          trial_ends_at: '2026-02-01T00:00:00Z',
          price_snapshot: null,
          current_period_end: null,
          cancelled_at: null,
        },
      ],
    })
    const wrapper = mount(AdminSubscriptionsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Firma A')
    expect(wrapper.text()).toContain('Probni period')
  })

  it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
    vi.mocked(listAdminSubscriptions).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          status: 'trialing',
          plan: null,
          trial_ends_at: '2026-02-01T00:00:00Z',
          price_snapshot: null,
          current_period_end: null,
          cancelled_at: null,
        },
      ],
    })
    const wrapper = mount(AdminSubscriptionsView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('th button').trigger('click')
    await flushPromises()

    expect(listAdminSubscriptions).toHaveBeenLastCalledWith(
      expect.objectContaining({ ordering: 'trial_ends_at' }),
    )
  })

  it('shows the current page and total page count', async () => {
    vi.mocked(listAdminSubscriptions).mockResolvedValue({
      count: 60,
      next: 'http://api/admin/subscriptions/?page=2',
      previous: null,
      results: [
        {
          id: 1,
          company_id: 1,
          company_name: 'Firma A',
          status: 'trialing',
          plan: null,
          trial_ends_at: '2026-02-01T00:00:00Z',
          price_snapshot: null,
          current_period_end: null,
          cancelled_at: null,
        },
      ],
    })
    const wrapper = mount(AdminSubscriptionsView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Strana 1 od 3')

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    await nextButton.trigger('click')
    await flushPromises()

    expect(listAdminSubscriptions).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
