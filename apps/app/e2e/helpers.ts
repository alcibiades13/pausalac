import { expect, type Page } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const API_BASE = 'http://localhost:8000/api/v1'

/**
 * Session-cookie + CSRF handling for API setup calls made via `page.request`
 * (shares cookies with the page's browser context, same as the real app's
 * own apiFetch — apps/app/src/lib/api.ts) — used to seed data fast for
 * parts of a flow that aren't themselves the thing under test.
 */
async function csrfToken(page: Page): Promise<string> {
  await page.request.get(`${API_BASE}/auth/csrf/`)
  const cookies = await page.context().cookies()
  const token = cookies.find((c) => c.name === 'csrftoken')?.value
  if (!token) throw new Error('csrftoken cookie not set after GET /auth/csrf/')
  return token
}

export async function apiPost(page: Page, path: string, body?: unknown, companyId?: number) {
  const token = await csrfToken(page)
  const response = await page.request.post(`${API_BASE}/${path}`, {
    data: body,
    headers: {
      'X-CSRFToken': token,
      ...(companyId ? { 'X-Company-Id': String(companyId) } : {}),
    },
  })
  if (!response.ok()) {
    throw new Error(`POST ${path} failed: ${response.status()} ${await response.text()}`)
  }
  return response.json()
}

export async function apiGet(page: Page, path: string, companyId?: number) {
  const response = await page.request.get(`${API_BASE}/${path}`, {
    headers: companyId ? { 'X-Company-Id': String(companyId) } : {},
  })
  if (!response.ok()) {
    throw new Error(`GET ${path} failed: ${response.status()} ${await response.text()}`)
  }
  return response.json()
}

export function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10000)}@e2e.pausalac.rs`
}

export function uniquePib(): string {
  // 9-digit numeric PIB, unique enough for one test run.
  return String(100000000 + Math.floor(Math.random() * 899999999)).slice(0, 9)
}

/** Registers a fresh user + company via the real API and returns both
 * ids — used as fast setup for flows where registration/onboarding
 * itself isn't the thing being tested. */
export async function registerWithCompany(
  page: Page,
  opts: { emailPrefix: string; companyName: string },
) {
  const email = uniqueEmail(opts.emailPrefix)
  const password = 's3cr3t-pass-123'
  await csrfToken(page)
  await apiPost(page, 'auth/register/', { email, password })
  const company = await apiPost(page, 'companies/', {
    name: opts.companyName,
    pib: uniquePib(),
  })
  return { email, password, company }
}

/**
 * Real automated accessibility scan (master prompt §55) via axe-core
 * against the currently-rendered page — run at a handful of
 * representative points in the existing critical-flow specs rather than
 * as its own dedicated suite, so it exercises real, already-authenticated
 * app state instead of isolated static pages. WCAG 2.0/2.1 A+AA rule
 * sets only — not asserting a conformance level beyond what §55 itself
 * asks for ("reasonable WCAG-oriented practices").
 */
export async function expectNoA11yViolations(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([])
}

/** Drives the real login form — used at the start of every UI-facing
 * flow so each test starts from a known, real, cookie-authenticated
 * browser state rather than injecting a session directly. */
export async function loginViaUi(page: Page, email: string, password: string) {
  await page.goto('/prijava')
  await page.getByLabel('Email adresa').fill(email)
  await page.getByLabel('Lozinka').fill(password)
  await page.getByRole('button', { name: 'Prijavi se' }).click()
  await expect(page).toHaveURL(/\/pocetna/)
}
