import { test, expect } from '@playwright/test'
import { apiPost, registerWithCompany } from './helpers'

test('recording a payment marks the invoice as paid', async ({ page }) => {
  const { company } = await registerWithCompany(page, {
    emailPrefix: 'payment',
    companyName: `Firma Payment ${Date.now()}`,
  })
  const client = await apiPost(page, 'clients/', { name: 'Klijent Payment' }, company.id)
  const today = new Date().toISOString().slice(0, 10)
  const invoice = await apiPost(
    page,
    'invoices/',
    {
      client: client.id,
      issue_date: today,
      due_date: today,
      service_date: today,
      items: [{ description: 'Usluga', quantity: '1', unit_price: '5000.00' }],
    },
    company.id,
  )
  await apiPost(page, `invoices/${invoice.id}/issue/`, undefined, company.id)

  await page.goto(`/fakture/${invoice.id}`)
  await expect(page.getByText('Izdata')).toBeVisible()

  await page.getByRole('button', { name: 'Evidentiraj uplatu' }).click()
  await page.getByLabel('Iznos').fill('5000')
  await page.getByLabel('Datum uplate').fill(today)
  await page.getByRole('button', { name: 'Sačuvaj uplatu' }).click()

  await expect(page.getByText('Plaćena')).toBeVisible()
})
