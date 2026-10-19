import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminUsersView from '../AdminUsersView.vue'
import {
  deactivateAdminUser,
  listAdminUsers,
  reactivateAdminUser,
  type AdminUser,
} from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminUsers: vi.fn<typeof listAdminUsers>(),
  deactivateAdminUser: vi.fn<typeof deactivateAdminUser>(),
  reactivateAdminUser: vi.fn<typeof reactivateAdminUser>(),
}))

function user(overrides: Partial<AdminUser> = {}): AdminUser {
  return {
    id: 1,
    email: 'marko@pausalac.rs',
    first_name: 'Marko',
    last_name: 'Markovic',
    is_active: true,
    is_staff: false,
    is_superuser: false,
    date_joined: '2026-01-01T00:00:00Z',
    email_verified_at: null,
    ...overrides,
  }
}

describe('AdminUsersView', () => {
  beforeEach(() => {
    vi.mocked(listAdminUsers).mockReset()
    vi.mocked(deactivateAdminUser).mockReset()
    vi.mocked(reactivateAdminUser).mockReset()
  })

  it('renders users returned by the service', async () => {
    vi.mocked(listAdminUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [user()],
    })
    const wrapper = mount(AdminUsersView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('marko@pausalac.rs')
    expect(wrapper.text()).toContain('Aktivan')
  })

  it('deactivates an active user and reloads the list', async () => {
    vi.mocked(listAdminUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [user()],
    })
    vi.mocked(deactivateAdminUser).mockResolvedValue(user({ is_active: false }))

    const wrapper = mount(AdminUsersView, { global: { plugins: [i18n] } })
    await flushPromises()

    // `th button` (the new sortable column header) is now the first
    // `<button>` on the page — target the row action button by its
    // text instead of position.
    await wrapper.findAll('button').find((b) => b.text() === 'Deaktiviraj')!.trigger('click')
    await flushPromises()

    expect(deactivateAdminUser).toHaveBeenCalledWith(1)
    expect(listAdminUsers).toHaveBeenCalledTimes(2)
  })

  it('reactivates a deactivated user', async () => {
    vi.mocked(listAdminUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [user({ is_active: false })],
    })
    vi.mocked(reactivateAdminUser).mockResolvedValue(user({ is_active: true }))

    const wrapper = mount(AdminUsersView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Deaktiviran')
    await wrapper.findAll('button').find((b) => b.text() === 'Reaktiviraj')!.trigger('click')
    await flushPromises()

    expect(reactivateAdminUser).toHaveBeenCalledWith(1)
  })

  it('re-fetches with an ordering param when a sortable column header is clicked', async () => {
    vi.mocked(listAdminUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [user()],
    })
    const wrapper = mount(AdminUsersView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('th button').trigger('click')
    await flushPromises()

    expect(listAdminUsers).toHaveBeenLastCalledWith(expect.objectContaining({ ordering: 'email' }))
  })

  it('shows the current page and total page count', async () => {
    vi.mocked(listAdminUsers).mockResolvedValue({
      count: 60,
      next: 'http://api/admin/users/?page=2',
      previous: null,
      results: [user()],
    })
    const wrapper = mount(AdminUsersView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Strana 1 od 3')

    const nextButton = wrapper.findAll('button').find((b) => b.text() === 'Sledeća')!
    await nextButton.trigger('click')
    await flushPromises()

    expect(listAdminUsers).toHaveBeenLastCalledWith(expect.objectContaining({ page: 2 }))
  })
})
