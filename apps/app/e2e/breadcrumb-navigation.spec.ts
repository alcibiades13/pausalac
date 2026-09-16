import { test, expect } from '@playwright/test'
import { registerWithCompany } from './helpers'

/**
 * Real proof the new TopHeader breadcrumb (AppBreadcrumb.vue, driven by
 * route.meta.section/breadcrumbKey — router/index.ts) actually resolves
 * labels and that its back button really navigates, not just that the
 * component renders in isolation (no unit test mounts it against a real
 * router with real route meta).
 *
 * Top-level routes (Fakture, Klijenti, ...) show no breadcrumb at all —
 * the sidebar already marks the active section and the page has its own
 * bare h1, so a breadcrumb repeating that same name read as redundant
 * (real user feedback). Only routes one level below a top-level section
 * (route.meta.section set) get a "Fakture / Nova faktura" style trail.
 */
test('the breadcrumb only appears on nested routes, with a working back button', async ({ page }) => {
  await registerWithCompany(page, {
    emailPrefix: 'breadcrumb-nav',
    companyName: `Firma Breadcrumb ${Date.now()}`,
  })

  await page.goto('http://localhost:5173/pocetna')
  // Two <header> elements exist (mobile-only + desktop-only, CSS-toggled
  // by breakpoint) — the desktop one is always the second in DOM order.
  const header = page.locator('header').last()

  // Top-level section page: no breadcrumb text, no back button — just
  // the page's own bare h1.
  await page.goto('http://localhost:5173/fakture')
  await expect(header.getByText('Fakture', { exact: true })).toHaveCount(0)
  await expect(header.getByLabel('Nazad')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Fakture', exact: true })).toBeVisible()

  // A subroute: section + leaf, with a working back button.
  await page.goto('http://localhost:5173/fakture/nova')
  await expect(header.getByText('Fakture', { exact: true })).toBeVisible()
  await expect(header.getByText('Nova faktura', { exact: true })).toBeVisible()
  await header.getByLabel('Nazad').click()
  await expect(page).toHaveURL(/\/fakture$/)
})
