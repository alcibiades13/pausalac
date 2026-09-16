import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import ObligationsView from '../ObligationsView.vue'
import {
  createTaxResolution,
  listTaxObligations,
  markObligationPaid,
  type TaxObligation,
  type TaxResolution,
} from '@/services/taxes'
import { i18n } from '@/i18n'

vi.mock('@/services/taxes', () => ({
  createTaxResolution: vi.fn<typeof createTaxResolution>(),
  listTaxObligations: vi.fn<typeof listTaxObligations>(),
  markObligationPaid: vi.fn<typeof markObligationPaid>(),
}))

function obligation(overrides: Partial<TaxObligation> = {}): TaxObligation {
  return {
    id: 1,
    resolution: 1,
    period_start: '2026-01-01',
    due_date: '2026-02-16',
    income_tax_amount: '10000.00',
    pio_amount: '24000.00',
    health_amount: '10300.00',
    unemployment_amount: '750.00',
    total_amount: '45050.00',
    status: 'pending',
    paid_at: null,
    ...overrides,
  }
}

function resolution(overrides: Partial<TaxResolution> = {}): TaxResolution {
  return {
    id: 1,
    effective_from: '2026-01-01',
    effective_until: '2026-01-31',
    tax_base: '100000.00',
    income_tax_amount: '10000.00',
    pio_amount: '24000.00',
    health_amount: '10300.00',
    unemployment_amount: '750.00',
    notes: '',
    created_at: '2026-01-01T00:00:00Z',
    rate_check_warnings: [],
    ...overrides,
  }
}

function mountView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })
  return mount(ObligationsView, { global: { plugins: [pinia, router, i18n] } })
}

describe('ObligationsView', () => {
  beforeEach(() => {
    vi.mocked(createTaxResolution).mockReset()
    vi.mocked(listTaxObligations).mockReset()
    vi.mocked(markObligationPaid).mockReset()
  })

  it('shows an empty state when there are no obligations', async () => {
    vi.mocked(listTaxObligations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Još nema obaveza.')
  })

  it('renders obligations with status and total', async () => {
    vi.mocked(listTaxObligations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [obligation()],
    })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('1. 1. 2026.')
    expect(wrapper.text()).toContain('Na čekanju')
    expect(wrapper.text()).toContain('45.050,00 RSD')
  })

  it('creates a resolution and shows rate-check warnings when present', async () => {
    vi.mocked(listTaxObligations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(createTaxResolution).mockResolvedValue(
      resolution({ rate_check_warnings: ['Iznos za porez na prihod (99999.00) odstupa...'] }),
    )
    const wrapper = mountView()
    await flushPromises()

    const dateInputs = wrapper.findAll('input[type="date"]')
    await dateInputs[0]!.setValue('2026-01-01')
    await dateInputs[1]!.setValue('2026-01-31')
    const numberInputs = wrapper.findAll('input[type="number"]')
    for (const input of numberInputs) {
      await input.setValue('10000')
    }
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createTaxResolution).toHaveBeenCalled()
    expect(wrapper.text()).toContain('odstupa')
  })

  it('marks an obligation as paid and reloads the list', async () => {
    vi.mocked(listTaxObligations).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [obligation()],
    })
    vi.mocked(markObligationPaid).mockResolvedValue(obligation({ status: 'paid' }))

    const wrapper = mountView()
    await flushPromises()

    const markPaidButton = wrapper.findAll('button').find((b) => b.text().includes('Označi kao plaćeno'))
    await markPaidButton!.trigger('click')
    await flushPromises()

    expect(markObligationPaid).toHaveBeenCalledWith(1)
    expect(listTaxObligations).toHaveBeenCalledTimes(2)
  })

  describe('deep link (master prompt §115)', () => {
    it('seeds the status filter from a ?status= query param', async () => {
      vi.mocked(listTaxObligations).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
      const pinia = createPinia()
      setActivePinia(pinia)
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [{ path: '/', component: { template: '<div/>' } }],
      })
      await router.push('/?status=overdue')
      const wrapper = mount(ObligationsView, { global: { plugins: [pinia, router, i18n] } })
      await flushPromises()

      expect(listTaxObligations).toHaveBeenCalledWith(expect.objectContaining({ status: 'overdue' }))
      const select = wrapper.find<HTMLSelectElement>('#obligation-status-filter')
      expect(select.element.value).toBe('overdue')
    })
  })
})
