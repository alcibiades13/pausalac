import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdminPlansView from '../AdminPlansView.vue'
import { createAdminPlan, listAdminPlans, updateAdminPlan } from '@/services/admin'

vi.mock('@/services/admin', () => ({
  listAdminPlans: vi.fn<typeof listAdminPlans>(),
  createAdminPlan: vi.fn<typeof createAdminPlan>(),
  updateAdminPlan: vi.fn<typeof updateAdminPlan>(),
}))

function plan() {
  return {
    id: 1,
    identifier: 'starter',
    name: 'Starter',
    price: '1500.00',
    currency: 'RSD',
    billing_interval: 'monthly' as const,
    entitlements: {},
    is_active: true,
  }
}

describe('AdminPlansView', () => {
  beforeEach(() => {
    vi.mocked(listAdminPlans).mockReset()
    vi.mocked(createAdminPlan).mockReset()
    vi.mocked(updateAdminPlan).mockReset()
  })

  it('renders plans returned by the service', async () => {
    vi.mocked(listAdminPlans).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [plan()],
    })
    const wrapper = mount(AdminPlansView)
    await flushPromises()
    expect(wrapper.text()).toContain('Starter')
    expect(wrapper.text()).toContain('1500.00 RSD')
  })

  it('opens a prefilled edit form and submits an update', async () => {
    vi.mocked(listAdminPlans).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [plan()],
    })
    vi.mocked(updateAdminPlan).mockResolvedValue(plan())

    const wrapper = mount(AdminPlansView)
    await flushPromises()

    const editButton = wrapper.findAll('button').find((b) => b.text() === 'Izmeni')!
    await editButton.trigger('click')
    await flushPromises()

    expect(wrapper.find('form').exists()).toBe(true)
    const inputs = wrapper.findAll('input')
    const priceField = inputs.find((i) => (i.element as HTMLInputElement).value === '1500.00')
    expect(priceField).toBeTruthy()
    await priceField!.setValue('1800.00')

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(updateAdminPlan).toHaveBeenCalledWith(1, expect.objectContaining({ price: '1800.00' }))
  })

  it('opens a blank create form from the "Novi plan" button', async () => {
    vi.mocked(listAdminPlans).mockResolvedValue({ count: 0, next: null, previous: null, results: [] })
    vi.mocked(createAdminPlan).mockResolvedValue(plan())

    const wrapper = mount(AdminPlansView)
    await flushPromises()

    const newButton = wrapper.findAll('button').find((b) => b.text().includes('Novi plan'))!
    await newButton.trigger('click')
    await flushPromises()

    expect(wrapper.find('form').exists()).toBe(true)
    const inputs = wrapper.findAll('input')
    expect((inputs[0]!.element as HTMLInputElement).value).toBe('')
  })
})
