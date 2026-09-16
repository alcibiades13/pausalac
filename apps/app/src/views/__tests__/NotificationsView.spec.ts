import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import NotificationsView from '../NotificationsView.vue'
import {
  listNotifications,
  markNotificationRead,
  type AppNotification,
} from '@/services/notifications'
import { i18n } from '@/i18n'

vi.mock('@/services/notifications', () => ({
  listNotifications: vi.fn<typeof listNotifications>(),
  markNotificationRead: vi.fn<typeof markNotificationRead>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
    { path: '/obaveze', name: 'obligations', component: { template: '<div/>' } },
  ],
})

function notification(overrides: Partial<AppNotification> = {}): AppNotification {
  return {
    id: 1,
    event_type: 'invoice_overdue',
    priority: 'attention',
    title: 'Faktura kasni',
    message: 'Faktura INV-2026-001 kasni 3 dana.',
    action_route: 'invoices',
    action_query: { status: 'overdue' },
    read_at: null,
    created_at: '2026-09-14T00:00:00Z',
    ...overrides,
  }
}

function mountView() {
  return mount(NotificationsView, { global: { plugins: [router, i18n] } })
}

describe('NotificationsView', () => {
  beforeEach(() => {
    vi.mocked(listNotifications).mockReset()
    vi.mocked(markNotificationRead).mockReset()
  })

  it('shows an empty state when there are no notifications', async () => {
    vi.mocked(listNotifications).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Nema obaveštenja.')
  })

  it('renders notifications with priority and unread indicator', async () => {
    vi.mocked(listNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [notification()],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Faktura kasni')
    expect(wrapper.text()).toContain('Pažnja')
    expect(wrapper.text()).toContain('Označi kao pročitano')
  })

  it('exposes an unread status as text, not just a visual dot/border (master prompt §55)', async () => {
    vi.mocked(listNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [notification()],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Nepročitano')
  })

  it('does not expose the unread text for an already-read notification', async () => {
    vi.mocked(listNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [notification({ read_at: '2026-09-14T01:00:00Z' })],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Nepročitano')
  })

  it('does not show the mark-read button for an already-read notification', async () => {
    vi.mocked(listNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [notification({ read_at: '2026-09-14T01:00:00Z' })],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Označi kao pročitano')
  })

  it('marks a notification read and updates it in place', async () => {
    vi.mocked(listNotifications).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [notification()],
    })
    vi.mocked(markNotificationRead).mockResolvedValue(notification({ read_at: '2026-09-14T01:00:00Z' }))

    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(markNotificationRead).toHaveBeenCalledWith(1)
    expect(wrapper.text()).not.toContain('Označi kao pročitano')
  })
})
