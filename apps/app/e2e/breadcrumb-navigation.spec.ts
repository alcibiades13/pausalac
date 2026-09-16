import { test, expect } from '@playwright/test'
import { registerWithCompany } from './helpers'

/**
 * Real proof the new TopHeader breadcrumb (AppBreadcrumb.vue, driven by
 * route.meta.section/breadcrumbKey — router/index.ts) actually resolves
 * labels and that its back button really navigates, not just that the
 * component renders in isolation (no unit test mounts it against a real
 * router with real route meta).
 */
test('the breadcrumb shows section/leaf labels and its back button returns to the list', async ({ page }) => {
  await registerWithCompany(page, {
    emailPrefix: 'breadcrumb-nav',
    companyName: `Firma Breadcrumb ${Date.now()}`,
  })

  await page.goto('http://localhost:5173/pocetna')
  // Two <header> elements exist (mobile-only + desktop-only, CSS-toggled
  // by breakpoint) — the desktop one is always the second in DOM order.
  const header = page.locator('header').last()

  // Top-level section page: no leaf, no back button.
  await page.goto('http://localhost:5173/fakture')
  await expect(header.getByText('Fakture', { exact: true })).toBeVisible()
  await expect(header.getByLabel('Nazad')).toHaveCount(0)

  // A subroute: section + leaf, with a working back button.
  await page.goto('http://localhost:5173/fakture/nova')
  await expect(header.getByText('Fakture', { exact: true })).toBeVisible()
  await expect(header.getByText('Nova faktura', { exact: true })).toBeVisible()
  await header.getByLabel('Nazad').click()
  await expect(page).toHaveURL(/\/fakture$/)
})
