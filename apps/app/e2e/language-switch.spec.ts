import { test, expect } from '@playwright/test'
import { registerWithCompany } from './helpers'

/**
 * Real, end-to-end proof of i18n-b's actual point: a logged-in user can
 * switch the app's language and it sticks. Nothing else in this suite
 * exercises the LanguageSwitcher/setLanguage() path — unit tests only
 * confirm individual strings render via `t()`, not that the whole
 * pipeline (native <select> → auth.setLanguage() → PATCH /auth/me/ →
 * vue-i18n's active locale) actually works together in a real browser,
 * or that the choice survives a reload (the real test of "persisted",
 * not just "changed in this tab").
 */
test('a user can switch the app language and it persists across a reload', async ({ page }) => {
  await registerWithCompany(page, {
    emailPrefix: 'lang-switch',
    companyName: `Firma Lang ${Date.now()}`,
  })

  await page.goto('http://localhost:5173/pocetna')
  await expect(page.getByText('Zahteva pažnju')).toBeVisible()

  await page.getByLabel('Izbor jezika').selectOption('en')
  await expect(page.getByRole('heading', { name: 'Needs attention' })).toBeVisible()
  await expect(page.getByText('Zahteva pažnju')).toHaveCount(0)

  // The choice must be the backend-persisted User.language, not just this
  // tab's in-memory vue-i18n state — reload and confirm it's still English.
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Needs attention' })).toBeVisible()
})
