import { execSync } from 'node:child_process'
import path from 'node:path'
import { test, expect } from '@playwright/test'
import { apiPost, registerWithCompany, expectNoA11yViolations } from './helpers'

/**
 * The overdue sweep is a Celery Beat task, not a user-triggered action
 * (apps/api/apps/invoices/tasks.py::mark_overdue_invoices_task) — its
 * manual/testing entry point is the `check_overdue_invoices` management
 * command (same one `docs/decisions-log.md`'s phase verifications have
 * used via curl+shell all project), run directly here since there's no
 * UI action that corresponds to "time passing."
 */
function runOverdueSweep() {
  const apiDir = path.resolve(process.cwd(), '../api')
  execSync('.venv/bin/python manage.py check_overdue_invoices', { cwd: apiDir, stdio: 'pipe' })
}

test('an invoice past its due date is shown as overdue once the sweep runs', async ({ page }) => {
  const { company } = await registerWithCompany(page, {
    emailPrefix: 'overdue',
    companyName: `Firma Overdue ${Date.now()}`,
  })
  const client = await apiPost(page, 'clients/', { name: 'Klijent Overdue' }, company.id)
  const today = new Date().toISOString().slice(0, 10)
  const pastDue = new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
  const invoice = await apiPost(
    page,
    'invoices/',
    {
      client: client.id,
      issue_date: today,
      due_date: pastDue,
      service_date: today,
      items: [{ description: 'Usluga', quantity: '1', unit_price: '3000.00' }],
    },
    company.id,
  )
  await apiPost(page, `invoices/${invoice.id}/issue/`, undefined, company.id)

  runOverdueSweep()

  await page.goto(`/fakture/${invoice.id}`)
  await expect(page.getByText('Kasni')).toBeVisible()

  // Real automated a11y scan (master prompt §55) on the invoice detail
  // page — badges, status-derived action buttons, a Dokumenti section.
  await expectNoA11yViolations(page)
})
