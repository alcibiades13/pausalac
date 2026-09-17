import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { i18n } from '@/i18n'
import AdminRulesView from '../AdminRulesView.vue'
import {
  approveAdminRegulatoryRule,
  createAdminRegulatoryRule,
  listAdminRegulatoryRules,
} from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminRegulatoryRules: vi.fn<typeof listAdminRegulatoryRules>(),
  createAdminRegulatoryRule: vi.fn<typeof createAdminRegulatoryRule>(),
  approveAdminRegulatoryRule: vi.fn<typeof approveAdminRegulatoryRule>(),
}))

function rule(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    identifier: 'turnover_limit',
    config: { amount: '6000000', currency: 'RSD' },
    effective_from: '2026-01-01',
    effective_until: null,
    source: 'Zakon o porezu na dohodak građana',
    version: 1,
    approval_status: 'unverified' as const,
    notes: '',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

describe('AdminRulesView', () => {
  beforeEach(() => {
    vi.mocked(listAdminRegulatoryRules).mockReset()
    vi.mocked(createAdminRegulatoryRule).mockReset()
    vi.mocked(approveAdminRegulatoryRule).mockReset()
  })

  it('renders rules with an unverified badge and an approve action', async () => {
    vi.mocked(listAdminRegulatoryRules).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [rule()],
    })
    const wrapper = mount(AdminRulesView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('turnover_limit')
    expect(wrapper.text()).toContain('Nepotvrđeno')
    expect(wrapper.text()).toContain('Potvrdi')
  })

  it('approves a rule and reloads the list', async () => {
    vi.mocked(listAdminRegulatoryRules).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [rule()],
    })
    vi.mocked(approveAdminRegulatoryRule).mockResolvedValue(rule({ approval_status: 'confirmed' }))

    const wrapper = mount(AdminRulesView, { global: { plugins: [i18n] } })
    await flushPromises()

    const approveButton = wrapper.findAll('button').find((b) => b.text() === 'Potvrdi')!
    await approveButton.trigger('click')
    await flushPromises()

    expect(approveAdminRegulatoryRule).toHaveBeenCalledWith(1)
    expect(listAdminRegulatoryRules).toHaveBeenCalledTimes(2)
  })

  it('does not offer approve for an already-confirmed rule', async () => {
    vi.mocked(listAdminRegulatoryRules).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [rule({ approval_status: 'confirmed' })],
    })
    const wrapper = mount(AdminRulesView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Potvrđeno')
    expect(wrapper.findAll('button').some((b) => b.text() === 'Potvrdi')).toBe(false)
  })

  it('submits a new rule version with parsed JSON config', async () => {
    vi.mocked(listAdminRegulatoryRules).mockResolvedValue({
      count: 0,
      next: null,
      previous: null,
      results: [],
    })
    vi.mocked(createAdminRegulatoryRule).mockResolvedValue(rule())

    const wrapper = mount(AdminRulesView, { global: { plugins: [i18n] } })
    await flushPromises()

    const newButton = wrapper.findAll('button').find((b) => b.text().includes('Nova verzija'))!
    await newButton.trigger('click')
    await flushPromises()

    const inputs = wrapper.findAll('input')
    await inputs[0]!.setValue('turnover_limit')
    // DatePicker (effective_from) renders two <input>s — a readonly
    // decorative display plus the real hidden type="date" input — so
    // "source" shifted from index 3 to 4.
    await inputs[4]!.setValue('Zakon X')

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createAdminRegulatoryRule).toHaveBeenCalledWith(
      expect.objectContaining({ identifier: 'turnover_limit', source: 'Zakon X' }),
    )
  })
})
