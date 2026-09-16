import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SubscriptionView from '../SubscriptionView.vue'
import { i18n } from '@/i18n'
import {
  listPlans,
  getCurrentSubscription,
  activatePlan,
  cancelSubscription,
  type Plan,
  type Subscription,
} from '@/services/subscriptions'

vi.mock('@/services/subscriptions', () => ({
  listPlans: vi.fn<typeof listPlans>(),
  getCurrentSubscription: vi.fn<typeof getCurrentSubscription>(),
  activatePlan: vi.fn<typeof activatePlan>(),
  cancelSubscription: vi.fn<typeof cancelSubscription>(),
}))

function plan(overrides: Partial<Plan> = {}): Plan {
  return {
    id: 1,
    identifier: 'starter',
    name: 'Starter',
    price: '1500.00',
    currency: 'RSD',
    billing_interval: 'monthly',
    entitlements: {},
    ...overrides,
  }
}

const PLANS = [
  plan(),
  plan({ id: 2, identifier: 'professional', name: 'Professional', price: '2000.00' }),
  plan({ id: 3, identifier: 'business', name: 'Business', price: '3000.00' }),
]

function subscription(overrides: Partial<Subscription> = {}): Subscription {
  return {
    id: 1,
    status: 'trialing',
    plan: null,
    trial_ends_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    price_snapshot: null,
    current_period_end: null,
    cancelled_at: null,
    ...overrides,
  }
}

describe('SubscriptionView', () => {
  beforeEach(() => {
    vi.mocked(listPlans).mockReset()
    vi.mocked(getCurrentSubscription).mockReset()
    vi.mocked(activatePlan).mockReset()
    vi.mocked(cancelSubscription).mockReset()
    vi.mocked(listPlans).mockResolvedValue(PLANS)
  })

  it('shows the trial status and days remaining', async () => {
    vi.mocked(getCurrentSubscription).mockResolvedValue(subscription())
    const wrapper = mount(SubscriptionView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Probni period')
    expect(wrapper.text()).toContain('ističe za 5 dan(a)')
  })

  it('renders all three plans', async () => {
    vi.mocked(getCurrentSubscription).mockResolvedValue(subscription())
    const wrapper = mount(SubscriptionView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Starter')
    expect(wrapper.text()).toContain('Professional')
    expect(wrapper.text()).toContain('Business')
    expect(wrapper.text()).toContain('1500.00')
  })

  it('activates a plan and reflects the new status', async () => {
    vi.mocked(getCurrentSubscription).mockResolvedValue(subscription())
    vi.mocked(activatePlan).mockResolvedValue(
      subscription({ status: 'active', plan: PLANS[1]! }),
    )

    const wrapper = mount(SubscriptionView, { global: { plugins: [i18n] } })
    await flushPromises()

    const buttons = wrapper.findAll('button').filter((b) => b.text() === 'Izaberi')
    await buttons[1]!.trigger('click')
    await flushPromises()

    expect(activatePlan).toHaveBeenCalledWith(2)
    expect(wrapper.text()).toContain('Aktivna')
    expect(wrapper.text()).toContain('Trenutni plan')
  })

  it('shows a cancel action once active and cancels it', async () => {
    vi.mocked(getCurrentSubscription).mockResolvedValue(
      subscription({ status: 'active', plan: PLANS[0]!, current_period_end: '2026-10-01T00:00:00Z' }),
    )
    vi.mocked(cancelSubscription).mockResolvedValue(subscription({ status: 'cancelled' }))

    const wrapper = mount(SubscriptionView, { global: { plugins: [i18n] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Sledeće obnavljanje: 1. 10. 2026.')
    const cancelButton = wrapper.findAll('button').find((b) => b.text() === 'Otkaži pretplatu')
    await cancelButton!.trigger('click')
    await flushPromises()

    expect(cancelSubscription).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Otkazana')
  })

  it('shows an error state with a retry option when loading fails', async () => {
    vi.mocked(getCurrentSubscription).mockRejectedValue(new Error('boom'))
    const wrapper = mount(SubscriptionView, { global: { plugins: [i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Ne možemo trenutno da učitamo pretplatu.')
  })
})
