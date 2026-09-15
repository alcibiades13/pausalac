import { test, expect } from '@playwright/test'
import { uniqueEmail, expectNoA11yViolations } from './helpers'

/**
 * Master prompt §64's first named flow: onboarding -> first invoice.
 * Fully UI-driven — registration and onboarding are the thing under
 * test here, unlike the other specs which fast-forward setup via the API.
 */
test('a new user can register, set up a company, add a client, and issue a first invoice', async ({
  page,
}) => {
  const email = uniqueEmail('onboarding')
  const password = 's3cr3t-pass-123'
  const companyName = `Firma Onboarding ${Date.now()}`
  const clientName = 'Prvi Klijent'

  await page.goto('/registracija')

  // Real automated a11y scan (master prompt §55) on an unauthenticated
  // auth-layout page — a different layout again from the dashboard/form
  // scans below.
  await expectNoA11yViolations(page)

  await page.getByLabel('Email adresa').fill(email)
  await page.getByLabel('Lozinka').fill(password)
  await page.getByRole('button', { name: 'Napravi nalog' }).click()
  await expect(page).toHaveURL(/\/pocetna/)

  // Zero-company bridge (HomeView.vue) — a fresh account has no company yet.
  await page.getByLabel('Naziv kompanije').fill(companyName)
  await page.getByRole('button', { name: 'Napravi kompaniju' }).click()
  // The company name renders both in the sidebar (visible at this
  // desktop viewport) and the mobile-only header (present in the DOM,
  // CSS-hidden here) — scope to the sidebar landmark to avoid a
  // strict-mode multi-match.
  await expect(page.getByRole('complementary').getByText(companyName)).toBeVisible()

  // Real automated a11y scan (master prompt §55) on the dashboard —
  // covers the app's main authenticated landing page, distinct from
  // the auth-only pages below.
  await expectNoA11yViolations(page)

  await page.goto('/klijenti/novi')
  await page.getByLabel('Naziv').fill(clientName)
  await page.getByRole('button', { name: 'Sačuvaj' }).click()
  // Saving a new client lands on its own detail page (Phase 6e), not
  // back on the list.
  await expect(page).toHaveURL(/\/klijenti\/\d+$/)
  await expect(page.getByText(clientName)).toBeVisible()

  await page.goto('/fakture/nova')
  await page.getByLabel('Klijent').selectOption({ label: clientName })
  const today = new Date().toISOString().slice(0, 10)
  await page.getByLabel('Datum izdavanja').fill(today)
  await page.getByLabel('Rok plaćanja').fill(today)
  await page.getByLabel('Datum prometa').fill(today)
  await page.getByLabel('Opis').fill('Konsultantske usluge')
  await page.getByLabel('Količina').fill('1')
  await page.getByLabel('Cena').fill('10000')

  // A second scan on a real, multi-field form page — different layout
  // (inputs, selects, a dynamic line-item grid) than the dashboard above.
  await expectNoA11yViolations(page)

  await page.getByRole('button', { name: 'Sačuvaj kao nacrt' }).click()

  await expect(page).toHaveURL(/\/fakture\/\d+$/)
  await expect(page.getByText('Nacrt')).toBeVisible()

  await page.getByRole('button', { name: 'Izdaj fakturu' }).click()
  await expect(page.getByText('Izdata')).toBeVisible()
})
