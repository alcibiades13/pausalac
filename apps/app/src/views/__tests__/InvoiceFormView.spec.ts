import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defineComponent } from 'vue'
import InvoiceFormView from '../InvoiceFormView.vue'
import { listClients, type Client } from '@/services/clients'
import { createInvoice, type Invoice } from '@/services/invoices'
import { i18n } from '@/i18n'

vi.mock('@/services/clients', () => ({
  listClients: vi.fn<typeof listClients>(),
}))

vi.mock('@/services/invoices', () => ({
  createInvoice: vi.fn<typeof createInvoice>(),
  getInvoice: vi.fn<() => Promise<never>>(),
  updateInvoice: vi.fn<() => Promise<never>>(),
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div/>' } },
    { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
    { path: '/fakture/:id', name: 'invoice-detail', component: { template: '<div/>' } },
    { path: '/klijenti/novi', name: 'client-new', component: { template: '<div/>' } },
  ],
})

function client(overrides: Partial<Client> = {}): Client {
  return {
    id: 1,
    client_type: 'company',
    name: 'Klijent A',
    tax_id: '',
    email: '',
    phone: '',
    address: '',
    country: 'RS',
    default_currency: 'RSD',
    notes: '',
    is_active: true,
    created_at: '',
    updated_at: '',
    ...overrides,
  }
}

function invoiceResult(): Invoice {
  return {
    id: 1,
    client: 1,
    client_name: 'Klijent A',
    client_email: '',
    invoice_number: null,
    status: 'draft',
    document_type: 'invoice',
    converted_from: null,
    converted_from_number: null,
    converted_to: null,
    converted_to_number: null,
    issue_date: '2026-01-01',
    due_date: '2026-01-15',
    service_date: '2026-01-01',
    currency: 'RSD',
    total: '1000.00',
    notes: '',
    issued_at: null,
    sent_at: null,
    paid_at: null,
    cancelled_at: null,
    created_at: '',
    updated_at: '',
    items: [],
  }
}

describe('InvoiceFormView', () => {
  beforeEach(() => {
    vi.mocked(listClients).mockReset()
    vi.mocked(createInvoice).mockReset()
    vi.mocked(listClients).mockResolvedValue({ count: 1, next: null, previous: null, results: [client()] })
  })

  it('defaults the line item type to service and submits it with the payload', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
    await flushPromises()

    const select = wrapper.find('select[id]:not([id="client"])')
    expect((select.element as HTMLSelectElement).value).toBe('service')

    await wrapper.find('input[type="text"]:not([readonly])').setValue('Konsalting')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [expect.objectContaining({ item_type: 'service', description: 'Konsalting' })],
      }),
    )
  })

  it('submits product when the type is changed', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
    await flushPromises()

    const select = wrapper.find('select[id]:not([id="client"])')
    await select.setValue('product')
    await wrapper.find('input[type="text"]:not([readonly])').setValue('Widget')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [expect.objectContaining({ item_type: 'product', description: 'Widget' })],
      }),
    )
  })

  it('defaults to document_type invoice and the "Nova faktura" heading when no type prop is given', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
    await flushPromises()
    expect(wrapper.text()).toContain('Nova faktura')

    await wrapper.find('input[type="text"]:not([readonly])').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(expect.objectContaining({ document_type: 'invoice' }))
  })

  it('shows the profaktura heading and sends document_type profaktura when created via that route', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, {
      props: { documentType: 'profaktura' },
      global: { plugins: [router, i18n] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Nova profaktura')

    await wrapper.find('input[type="text"]:not([readonly])').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(
      expect.objectContaining({ document_type: 'profaktura' }),
    )
  })

  it('shows the avans heading and sends document_type avans when created via that route', async () => {
    vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
    const wrapper = mount(InvoiceFormView, {
      props: { documentType: 'avans' },
      global: { plugins: [router, i18n] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Novi avans')

    await wrapper.find('input[type="text"]:not([readonly])').setValue('X')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(createInvoice).toHaveBeenCalledWith(expect.objectContaining({ document_type: 'avans' }))
  })

  describe('?client= prepopulation (master prompt §94)', () => {
    beforeEach(async () => {
      vi.mocked(listClients).mockResolvedValue({
        count: 2,
        next: null,
        previous: null,
        results: [client({ id: 1, name: 'Klijent A' }), client({ id: 2, name: 'Klijent B' })],
      })
    })

    it('preselects the client named in the ?client= query param', async () => {
      await router.push('/?client=2')
      vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
      const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
      await flushPromises()

      const clientSelect = wrapper.find<HTMLSelectElement>('#client')
      expect(clientSelect.element.value).toBe('2')
    })

    it('falls back to the first client when ?client= does not match any client', async () => {
      await router.push('/?client=999')
      vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
      const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
      await flushPromises()

      const clientSelect = wrapper.find<HTMLSelectElement>('#client')
      expect(clientSelect.element.value).toBe('1')
    })

    it('falls back to the first client when there is no ?client= query param', async () => {
      await router.push('/')
      vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
      const wrapper = mount(InvoiceFormView, { global: { plugins: [router, i18n] } })
      await flushPromises()

      const clientSelect = wrapper.find<HTMLSelectElement>('#client')
      expect(clientSelect.element.value).toBe('1')
    })
  })

  describe('unsaved-changes guard', () => {
    // A fresh router per test — the guard tests navigate through
    // router-view (unlike the tests above, which mount InvoiceFormView
    // directly), so reusing the module-level `router` would leak a
    // still-mounted, still-dirty component instance across tests.
    function buildGuardRouter() {
      return createRouter({
        history: createMemoryHistory(),
        routes: [
          { path: '/fakture', name: 'invoices', component: { template: '<div/>' } },
          { path: '/fakture/nova', name: 'invoice-new', component: InvoiceFormView },
          {
            path: '/fakture/:id',
            name: 'invoice-detail',
            component: { template: '<div/>' },
          },
          { path: '/klijenti/novi', name: 'client-new', component: { template: '<div/>' } },
        ],
      })
    }

    it('prompts before leaving a dirty form', async () => {
      const guardRouter = buildGuardRouter()
      await guardRouter.push('/fakture/nova')
      await guardRouter.isReady()
      const RootComponent = defineComponent({ template: '<router-view />' })
      const wrapper = mount(RootComponent, { global: { plugins: [guardRouter, i18n] } })
      await flushPromises()

      await wrapper.find('input[type="text"]:not([readonly])').setValue('Konsalting')

      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
      await guardRouter.push('/fakture')
      await flushPromises()

      expect(confirmSpy).toHaveBeenCalled()
      expect(guardRouter.currentRoute.value.name).toBe('invoice-new')
      confirmSpy.mockRestore()
    })

    it('does not prompt when navigating away right after a successful save', async () => {
      vi.mocked(createInvoice).mockResolvedValue(invoiceResult())
      const guardRouter = buildGuardRouter()
      await guardRouter.push('/fakture/nova')
      await guardRouter.isReady()
      const RootComponent = defineComponent({ template: '<router-view />' })
      const wrapper = mount(RootComponent, { global: { plugins: [guardRouter, i18n] } })
      await flushPromises()

      const confirmSpy = vi.spyOn(window, 'confirm')
      await wrapper.find('input[type="text"]:not([readonly])').setValue('Konsalting')
      await wrapper.find('form').trigger('submit.prevent')
      await flushPromises()

      expect(confirmSpy).not.toHaveBeenCalled()
      expect(guardRouter.currentRoute.value.name).toBe('invoice-detail')
      confirmSpy.mockRestore()
    })
  })
})
