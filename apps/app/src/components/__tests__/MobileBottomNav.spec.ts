import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import MobileBottomNav from '../MobileBottomNav.vue'

const stub = { template: '<div/>' }
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: stub },
    { path: '/fakture', name: 'invoices', component: stub },
    { path: '/fakture/nova', name: 'invoice-new', component: stub },
    { path: '/fakture/nova/profaktura', name: 'invoice-new-profaktura', component: stub },
    { path: '/fakture/nova/avans', name: 'invoice-new-avans', component: stub },
    { path: '/fakture/:id/izmeni', name: 'invoice-edit', component: stub },
    { path: '/fakture/:id', name: 'invoice-detail', component: stub },
    { path: '/finansije', name: 'finansije', component: stub },
    { path: '/limiti', name: 'limits', component: stub },
    { path: '/kpo', name: 'kpo', component: stub },
    { path: '/obaveze', name: 'obligations', component: stub },
    { path: '/vise', name: 'vise', component: stub },
    { path: '/klijenti', name: 'clients', component: stub },
    { path: '/klijenti/novi', name: 'client-new', component: stub },
    { path: '/klijenti/:id', name: 'client-edit', component: stub },
    { path: '/dokumenti', name: 'documents', component: stub },
    { path: '/racunovodja', name: 'accounting', component: stub },
    { path: '/organizacija', name: 'accounting-organization', component: stub },
    { path: '/podesavanja', name: 'settings', component: stub },
    { path: '/obavestenja', name: 'notifications', component: stub },
    { path: '/pretplata', name: 'subscription', component: stub },
  ],
})

let wrapper: ReturnType<typeof mount> | null = null

describe('MobileBottomNav', () => {
  beforeEach(async () => {
    await router.push({ name: 'home' })
    await router.isReady()
  })

  afterEach(() => {
    // Teleport targets the real document.body regardless of where the
    // wrapper mounts — without unmounting, a sheet opened in one test
    // would still be in the DOM for the next test's queries.
    wrapper?.unmount()
    wrapper = null
  })

  it('renders the four tabs with the right links', async () => {
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    const nav = wrapper.get('nav')
    const links = nav.findAll('a')
    expect(links.map((l) => l.text())).toEqual(['Početna', 'Fakture', 'Finansije', 'Više'])
  })

  it('highlights only the active tab, and the rest stay inactive', async () => {
    await router.push({ name: 'invoices' })
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    const links = wrapper.get('nav').findAll('a')
    const active = links.find((l) => l.text() === 'Fakture')!
    const inactive = links.find((l) => l.text() === 'Početna')!
    expect(active.classes()).toContain('text-primary')
    expect(inactive.classes()).not.toContain('text-primary')
    expect(inactive.classes()).toContain('text-text-secondary')
  })

  it('highlights Finansije when on a grouped sub-route like limits', async () => {
    await router.push({ name: 'limits' })
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    const active = wrapper.get('nav').findAll('a').find((l) => l.text() === 'Finansije')!
    expect(active.classes()).toContain('text-primary')
  })

  it('highlights Više when on a grouped sub-route like settings', async () => {
    await router.push({ name: 'settings' })
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    const active = wrapper.get('nav').findAll('a').find((l) => l.text() === 'Više')!
    expect(active.classes()).toContain('text-primary')
  })

  it('opens the quick-create sheet with exactly the four non-excluded items in order', async () => {
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.get('[aria-label="Brza akcija"]').trigger('click')
    await flushPromises()

    const sheetLinks = Array.from(
      document.body.querySelectorAll('.fixed.inset-0.z-30 a'),
    ) as HTMLAnchorElement[]
    expect(sheetLinks.map((l) => l.textContent?.trim())).toEqual([
      'Nova faktura',
      'Profaktura',
      'Avans',
      'Novi klijent',
    ])
    // The two already-excluded FAB items (§40/§76-78) must never appear.
    const allText = sheetLinks.map((l) => l.textContent?.trim()).join(' ')
    expect(allText).not.toContain('Fiskalni račun')
    expect(allText).not.toContain('Novi trošak')
  })

  it('closes the sheet when the backdrop is clicked', async () => {
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.get('[aria-label="Brza akcija"]').trigger('click')
    await flushPromises()
    expect(document.body.querySelector('.fixed.inset-0.z-30')).toBeTruthy()

    const backdrop = document.body.querySelector<HTMLElement>('.fixed.inset-0.z-30 > .bg-navy\\/40')!
    backdrop.click()
    await flushPromises()
    expect(document.body.querySelector('.fixed.inset-0.z-30')).toBeFalsy()
  })

  it('closes the sheet on navigation', async () => {
    wrapper = mount(MobileBottomNav, { global: { plugins: [router] } })
    await flushPromises()

    await wrapper.get('[aria-label="Brza akcija"]').trigger('click')
    await flushPromises()
    expect(document.body.querySelector('.fixed.inset-0.z-30')).toBeTruthy()

    await router.push({ name: 'invoices' })
    await flushPromises()
    expect(document.body.querySelector('.fixed.inset-0.z-30')).toBeFalsy()
  })
})
