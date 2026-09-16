import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AccountingView from '../AccountingView.vue'
import { i18n } from '@/i18n'
import {
  listClientConnections,
  acceptConnection,
  declineConnection,
  revokeConnection,
  type ClientConnection,
} from '@/services/accounting'

vi.mock('@/services/accounting', () => ({
  listClientConnections: vi.fn<typeof listClientConnections>(),
  acceptConnection: vi.fn<typeof acceptConnection>(),
  declineConnection: vi.fn<typeof declineConnection>(),
  revokeConnection: vi.fn<typeof revokeConnection>(),
}))

function connection(overrides: Partial<ClientConnection> = {}): ClientConnection {
  return {
    id: 1,
    organization: 1,
    organization_name: 'Agencija Prime',
    granted_role: 'accountant',
    status: 'pending',
    created_at: '2026-09-14T00:00:00Z',
    accepted_at: null,
    revoked_at: null,
    ...overrides,
  }
}

describe('AccountingView', () => {
  beforeEach(() => {
    vi.mocked(listClientConnections).mockReset()
    vi.mocked(acceptConnection).mockReset()
    vi.mocked(declineConnection).mockReset()
    vi.mocked(revokeConnection).mockReset()
  })

  it('shows an empty state when there are no connections', async () => {
    vi.mocked(listClientConnections).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mount(AccountingView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Još nema povezane računovodstvene agencije.')
  })

  it('shows accept/decline actions for a pending connection', async () => {
    vi.mocked(listClientConnections).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [connection()],
    })
    const wrapper = mount(AccountingView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Agencija Prime')
    expect(wrapper.text()).toContain('Na čekanju')
    expect(wrapper.text()).toContain('Prihvati')
    expect(wrapper.text()).toContain('Odbij')
  })

  it('accepts a connection and reloads the list', async () => {
    vi.mocked(listClientConnections).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [connection()],
    })
    vi.mocked(acceptConnection).mockResolvedValue(connection({ status: 'active' }))

    const wrapper = mount(AccountingView, { global: { plugins: [i18n] } })
    await flushPromises()

    const acceptButton = wrapper.findAll('button').find((b) => b.text() === 'Prihvati')
    await acceptButton!.trigger('click')
    await flushPromises()

    expect(acceptConnection).toHaveBeenCalledWith(1)
    expect(listClientConnections).toHaveBeenCalledTimes(2)
  })

  it('shows a revoke action for an active connection', async () => {
    vi.mocked(listClientConnections).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [connection({ status: 'active' })],
    })
    const wrapper = mount(AccountingView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Aktivna')
    expect(wrapper.text()).toContain('Opozovi pristup')
  })

  it('revokes an active connection and reloads the list', async () => {
    vi.mocked(listClientConnections).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [connection({ status: 'active' })],
    })
    vi.mocked(revokeConnection).mockResolvedValue(connection({ status: 'revoked' }))

    const wrapper = mount(AccountingView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(revokeConnection).toHaveBeenCalledWith(1)
    expect(listClientConnections).toHaveBeenCalledTimes(2)
  })
})
