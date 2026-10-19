import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LimitTracker from '../LimitTracker.vue'
import type { LimitTrackerData } from '@/services/limits'
import { i18n } from '@/i18n'

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

describe('LimitTracker', () => {
  it('renders the label, percentage and remaining amount', () => {
    const wrapper = mount(LimitTracker, { global: { plugins: [i18n] }, props: { label: 'Paušalni limit', tracker: tracker() } })
    expect(wrapper.text()).toContain('Paušalni limit')
    expect(wrapper.text()).toContain('47%')
    expect(wrapper.text()).toContain('kalendarska godina')
  })

  it('keeps a real space before the "/" in the current/threshold fraction', () => {
    // Regression: adjacent inline elements with only template
    // whitespace between them can collapse to zero space, producing
    // "... RSD/ 6.000.000,00 RSD" with no gap before the slash.
    const wrapper = mount(LimitTracker, { global: { plugins: [i18n] }, props: { label: 'Paušalni limit', tracker: tracker() } })
    expect(wrapper.text()).toContain('RSD /')
  })

  it('shows the projection line when present, suffixed as an estimate', () => {
    const wrapper = mount(LimitTracker, {
      global: { plugins: [i18n] },
      props: {
        label: 'Paušalni limit',
        tracker: tracker({ projection: { estimated_period_end: '5200000.00', label: 'procena' } }),
      },
    })
    expect(wrapper.text()).toContain('procena')
  })

  it('omits the projection line when absent', () => {
    const wrapper = mount(LimitTracker, { global: { plugins: [i18n] }, props: { label: 'PDV prag', tracker: tracker({ projection: null }) } })
    expect(wrapper.text()).not.toContain('Procena do kraja perioda')
  })

  it('shows the trailing-12-months period label for the VAT tracker', () => {
    const wrapper = mount(LimitTracker, {
      global: { plugins: [i18n] },
      props: {
        label: 'PDV prag',
        tracker: tracker({ period: { type: 'trailing_12_months', start: '2025-09-14', end: '2026-09-14' } }),
      },
    })
    expect(wrapper.text()).toContain('poslednjih 12 meseci')
  })
})
