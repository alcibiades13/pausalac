import { test, expect } from '@playwright/test'
import { registerWithCompany } from './helpers'

/**
 * Real, cross-origin verification of apps/web's useAuthStatus.ts — a
 * logged-in-on-the-app visitor landing on the marketing site (a
 * different origin, :3000 vs :5173) should see "Idi u aplikaciju"
 * instead of "Registruj se"/"Probaj besplatno". This works today
 * without any subdomain setup because cookies were never port-scoped —
 * SameSite=Lax + CORS_ALLOW_CREDENTIALS (config/settings/dev.py) is
 * enough for a same-site (same registrable domain "localhost"),
 * different-origin (different port) request to carry the session
 * cookie. In staging/production, once real subdomains exist,
 * SESSION_COOKIE_DOMAIN extends the same mechanism across them.
 */
test('a visitor logged into the app is recognized by the marketing site on a different port', async ({
  page,
}) => {
  await registerWithCompany(page, {
    emailPrefix: 'marketing-handoff',
    companyName: `Firma Handoff ${Date.now()}`,
  })

  await page.goto('http://localhost:3000/')
  await expect(page.getByRole('link', { name: 'Idi u aplikaciju' })).toBeVisible()
  await expect(page.locator('header').getByRole('link', { name: 'Probaj besplatno' })).toHaveCount(0)
})

test('an anonymous visitor sees the normal register/login CTAs', async ({ page, context }) => {
  await context.clearCookies()
  await page.goto('http://localhost:3000/')
  await expect(page.getByRole('link', { name: 'Probaj besplatno' }).first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Idi u aplikaciju' })).toHaveCount(0)
})
