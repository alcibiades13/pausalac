import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LimitsView from '../LimitsView.vue'
import { getLimits, simulateLimits } from '@/services/limits'
import type { LimitTrackerData, Limits } from '@/services/limits'
import { i18n } from '@/i18n'

vi.mock('@/services/limits', () => ({
  getLimits: vi.fn<typeof getLimits>(),
  simulateLimits: vi.fn<typeof simulateLimits>(),
}))

function tracker(overrides: Partial<LimitTrackerData> = {}): LimitTrackerData {
  return {
    identifier: 'pausal_turnover_limit',
    period: { type: 'calendar_year', start: '2026-01-01', end: '2026-12-31' },
    threshold: '6000000.00',
    current: '2840000.00',
    currency: 'RSD',
    percentage: 47,
    remaining: '3160000.00',
    warning_level: 'ok',
    projection: null,
    approval_status: 'unverified',
    ...overrides,
  }
}

function limits(): Limits {
  return {
    pausal_limit: tracker(),
    vat_threshold: tracker({
      identifier: 'vat_registration_threshold',
      period: { type: 'trailing_12_months', start: '2025-09-14', end: '2026-09-14' },
      threshold: '8000000.00',
      percentage: 12,
    }),
  }
}

describe('LimitsView', () => {
  beforeEach(() => {
    vi.mocked(getLimits).mockReset()
    vi.mocked(simulateLimits).mockReset()
  })

  it('renders both trackers from getLimits', async () => {
    vi.mocked(getLimits).mockResolvedValue(limits())
    const wrapper = mount(LimitsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Paušalni limit')
    expect(wrapper.text()).toContain('PDV prag')
    expect(wrapper.text()).toContain('47%')
    expect(wrapper.text()).toContain('12%')
  })

  it('submits the what-if form and renders before/after', async () => {
    vi.mocked(getLimits).mockResolvedValue(limits())
    vi.mocked(simulateLimits).mockResolvedValue({
      before: limits(),
      after: {
        pausal_limit: tracker({ current: '3640000.00', percentage: 61, remaining: '2360000.00' }),
        vat_threshold: tracker({
          identifier: 'vat_registration_threshold',
          period: { type: 'trailing_12_months', start: '2025-09-14', end: '2026-09-14' },
          threshold: '8000000.00',
          percentage: 22,
        }),
      },
    })
    const wrapper = mount(LimitsView, { global: { plugins: [i18n] } })
    await flushPromises()

    await wrapper.find('input').setValue('800000.00')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(simulateLimits).toHaveBeenCalledWith('800000.00')
    expect(wrapper.text()).toContain('Simulacija')
    expect(wrapper.text()).toContain('61%')
    expect(wrapper.text()).toContain('22%')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(getLimits).mockRejectedValue(new Error('boom'))
    const wrapper = mount(LimitsView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno da učitamo limite.')
  })
})
