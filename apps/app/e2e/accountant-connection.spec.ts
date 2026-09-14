import { test, expect } from '@playwright/test'
import { apiPost, registerWithCompany, uniqueEmail } from './helpers'

/**
 * Two real, independent identities — the accounting org admin and the
 * client company owner — so this uses two separate browser contexts
 * (two isolated cookie jars) rather than logging in and out on one page.
 */
test('an accounting org can connect to a client company, and the client can accept it', async ({
  browser,
}) => {
  const adminContext = await browser.newContext()
  const adminPage = await adminContext.newPage()
  const adminEmail = uniqueEmail('org-admin')
  const adminPassword = 's3cr3t-pass-123'
  await adminPage.goto('/')
  await apiPost(adminPage, 'auth/register/', { email: adminEmail, password: adminPassword })
  const org = await apiPost(adminPage, 'accounting/organizations/', {
    name: `Agencija E2E ${Date.now()}`,
  })

  const ownerContext = await browser.newContext()
  const ownerPage = await ownerContext.newPage()
  const { company } = await registerWithCompany(ownerPage, {
    emailPrefix: 'org-client',
    companyName: `Firma Klijent E2E ${Date.now()}`,
  })

  // Org admin invites the client by PIB (AccountingOrganizationView.vue).
  await adminPage.goto('/organizacija')
  await adminPage.getByLabel('PIB klijenta').fill(company.pib)
  await adminPage.getByRole('button', { name: 'Pozovi klijenta' }).click()
  await expect(adminPage.getByRole('heading', { name: 'Na čekanju' })).toBeVisible()

  // Client owner sees and accepts the request (AccountingView.vue, "Moj računovođa").
  await ownerPage.goto('/racunovodja')
  await expect(ownerPage.getByText(org.name)).toBeVisible()
  await ownerPage.getByRole('button', { name: 'Prihvati' }).click()
  await expect(ownerPage.getByText('Aktivna')).toBeVisible()

  // The connection now shows as active in the org's own portfolio table too.
  await adminPage.goto('/organizacija')
  await expect(adminPage.getByText(company.name)).toBeVisible()

  await adminContext.close()
  await ownerContext.close()
})
