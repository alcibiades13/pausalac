import { test, expect } from '@playwright/test'
import { registerWithCompany } from './helpers'

test('a fresh company starts on a trial and can activate a real plan', async ({ page }) => {
  await registerWithCompany(page, {
    emailPrefix: 'trial',
    companyName: `Firma Trial ${Date.now()}`,
  })

  await page.goto('/pretplata')
  await expect(page.getByText(/ističe za \d+ dan/)).toBeVisible()

  // Seeded plans (apps/subscriptions/migrations/0002_seed_plans.py) — any
  // of the three "Izaberi" buttons proves the same activation path.
  await page.getByRole('button', { name: 'Izaberi' }).first().click()
  await expect(page.getByText('Aktivna')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Otkaži pretplatu' })).toBeVisible()
})
