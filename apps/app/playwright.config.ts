import { defineConfig, devices } from '@playwright/test'

/**
 * E2E suite for the spec's own named critical flows (master prompt §64):
 * onboarding->first invoice, invoice payment, overdue invoice,
 * subscription/trial, accountant connection.
 *
 * Assumes the real stack is already running — `pnpm dev` from the repo
 * root (docker compose + Django + Celery + Vite) — same stack every
 * phase's manual curl-based E2E verification has used all project. No
 * `webServer` auto-start here: orchestrating docker-compose + migrations
 * + two dev servers is more than Playwright's single-command webServer
 * feature is meant for; CI (.github/workflows/ci.yml) does that
 * orchestration explicitly instead.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // tests share one backend/DB — avoid cross-test interference
  // Every test registers at least one account against the real "auth"
  // rate-limit scope (config/settings/base.py, Phase 6a) — running specs
  // across parallel workers burst-consumes that shared per-IP budget and
  // produces real, environment-dependent 429s (found by actually running
  // this suite, not assumed). One worker keeps total register/login
  // volume predictable regardless of how many spec files exist.
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['list']] : [['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})
