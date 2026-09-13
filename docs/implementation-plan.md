# Pausalac SaaS — Phase 0 Implementation Plan

## Context

The repo (`/home/alcibiades/Projects/pausalac`) is currently empty except for three specification documents: `Pausalac.md`, `pausalac-product-blueprint.md`, and `pausalni_product_blueprint.docx`. This is a greenfield, production-grade SaaS for Serbian *paušalni preduzetnici* (flat-rate taxed entrepreneurs), to be built by the user and one colleague, pushed to git. The user's own master prompt (embedded in the two `.md` files) explicitly requires a **Phase 0 discovery + implementation plan** before any significant code is written — this document is that deliverable, plus a scoped, low-risk first execution step (repo/tooling scaffold) to hand off to the team immediately after approval.

**Documentation finding (resolved with user):** the two canonical source documents are now confirmed as `Pausalac.md` (Master Development Prompt, 130 sections) and `pausalac-blueprint.md` (Product Blueprint, 28 sections — a clean markdown transcription of the original docx, verified word-for-word identical to it). `pausalac-product-blueprint.md` (an earlier mislabeled duplicate of the master prompt) and `pausalni_product_blueprint.docx` (superseded by the clean md transcription) are redundant. Per the user's instruction, these two source docs are what the team will maintain going forward — no content contradictions exist between them (the blueprint is a shorter, higher-level restatement of the same product).

**Key strategic detail from the blueprint (§1, §13):** the client has an existing accounting firm. The product must be designed from day one as **two connected surfaces** — the paušalac-facing app and an accountant "command center" — not as an afterthought. This elevates the Accountant Platform (already in MVP scope per the master prompt) to a first-class architectural concern, not a bolt-on.

## Scope of this plan

This plan covers:
1. The discovery/architecture write-up (this document, committed to the repo).
2. A decisions log capturing conventions I'm choosing per the master prompt's own §81 rule ("if it doesn't touch money/legal/tax/security/irreversible data, decide and document — don't block").
3. A concrete, sequenced roadmap (Phase 1–7) restating the master prompt's phases with actionable detail.
4. An explicit list of things that must **not** be guessed (regulatory numbers, SEF/fiscalization specifics, exact pricing) — flagged per §81/§82 for confirmation before they're encoded as real rules.
5. A scoped **first execution step** ("Phase 1a — Bootstrap") to run immediately after approval: repo tooling, monorepo layout, Docker Compose dev stack, and empty-but-runnable Django/Vue/Nuxt skeletons. This deliberately stops **before** auth, tenancy, RBAC, and audit infrastructure — those touch security and data-model decisions that deserve their own focused plan/review pass once the skeleton exists.

Everything beyond Phase 1a (auth, domain models, invoicing, KPO, limits, etc.) is sequenced but **not started** in this pass.

## Repository & tooling decisions (documented per §81, non-blocking)

- **Monorepo** with **pnpm workspaces**. One repo for `api`, the product app, the marketing site, and shared frontend packages — matches "modular monolith" thinking and keeps the two-person team from juggling repo sprawl.
- Layout:
  ```
  pausalac/
    apps/
      api/     # Django + DRF (modular monolith, one Django app per domain)
      app/     # Vue 3 + TS + Vite — the authenticated product (per blueprint §14.1: Vue for the app itself)
      web/     # Nuxt 4 — public marketing/landing site (per blueprint §14.1: "Nuxt for the marketing layer")
    packages/
      ui/      # shared design tokens + component primitives consumed by app/ and web/
      config/  # shared eslint/tsconfig/tailwind config
    docs/
      source/            # the 3 original spec docs (untouched) + md transcription of the docx
      implementation-plan.md
      decisions-log.md
    docker-compose.yml   # postgres, redis, minio (S3-compatible), mailhog (dev email)
    .env.example
  ```
- **Django**: apps-per-domain matching master prompt §44: `accounts, companies, clients, invoices, payments, kpo, limits, taxes, documents, notifications, analytics, subscriptions, integrations, audit` (seams only for `sef`, `fiscalization`, `banking`, `ai` — no implementation).
- **Local dev**: Docker Compose for Postgres 16, Redis, MinIO (S3-compatible object storage per §26), MailHog (catch dev emails per §107). Django/Celery run natively or via compose — will scaffold compose services for both and let the team choose.
- **Versions**: Python 3.12, Node 22 LTS, Django 5.x + DRF, Vue 3 + Vite, Nuxt 4, Tailwind 3/4 with the exact palette/tokens from blueprint §18 (`#172033`, `#F7F8FA`, `#4F46E5`, `#16A34A`, `#D97706`, `#DC2626`, `#64748B`, `#E2E8F0`, Inter font).
- **Git**: single repo, `main` branch, Conventional Commits, `.gitignore` for Python/Node/Django/env files. No remote push in this step — team can add their own remote.
- **CI**: a minimal GitHub Actions skeleton (lint + placeholder test job) added now so the pattern exists; real test suites arrive with the domains that need them (§70).

## Architecture summary

- **Modular monolith** (Django), not microservices — matches §44.
- **Multi-tenancy**: every tenant-owned model FK's to `Company`; enforced via a shared queryset-scoping mixin/manager, never frontend-only filtering (§47). Cross-tenant access gets explicit tests from the start.
- **Financial event / ledger layer** (§21, blueprint §15): a central `FinancialEvent` model (append-only) is the single source of truth that Dashboard, KPO, and Limits all read from — no independent calculation paths.
- **Rules engine** (§25, blueprint §16): regulatory numbers (annual turnover limit, rolling-365 threshold, thresholds like 70/85/95%, due dates) live in a versioned `RegulatoryRule` table (`identifier`, `value/config`, `effective_from/until`, `source`, `version`, `approval_status`) — never hardcoded in business logic.
- **Audit log**: backend-level, model-agnostic (`actor, timestamp, entity, entity_id, action, old_value, new_value, source, metadata`), independent of any frontend call.
- **RBAC**: roles per §30 (`Client Owner, Accountant, Accountant Admin, System Admin`) with granular permission checks, backend-authoritative.
- **Integration seams, not fakes**: `SEFProvider`, NBS `get_rate(currency, date)`, and a fiscalization seam are defined as interfaces now; no mock treated as production (§39, §40, §123).
- **Money**: `Decimal`/`NUMERIC` only, never floats (§46).

## Core domain model (MVP-relevant entities, for the follow-up design pass)

`Company` (tenant), `Membership` (user↔company + role), `Client`, `Invoice` + `InvoiceLineItem`, `Payment`, `FinancialEvent`, `KPOEntry`, `RegulatoryRule`, `TaxObligation`, `Document`, `Notification`, `AccountingOrganization` + `AccountingRelationship` (company↔accountant, with status/permissions/invitation), `Subscription`/`Plan`/`Entitlement`, `AuditLogEntry`. This list is a preview — the full ERD is a Phase 1b deliverable, not finalized here.

## Roadmap (restating master prompt §80/§129 concretely)

| Phase | Content |
|---|---|
| **0 — Discovery** ✅ | Architecture summary, decisions log, roadmap |
| **1a — Bootstrap** ✅ | Monorepo, Docker Compose, empty Django/Vue/Nuxt skeletons, CI skeleton |
| **1b — Auth/tenant/RBAC/audit backend** ✅ | Custom User model, session+CSRF auth (register/verify/login/logout/password-reset), Company/Membership tenant model, RBAC (`ROLE_PERMISSIONS`), tenant-scoping mechanism, append-only audit log + `AuditService`. Backend only — see `docs/decisions-log.md`. |
| **1c — Frontend foundation** ✅ | `packages/ui` primitives (Button/Input/Card/Alert), auth store + API client in `apps/app`, login/register/forgot-password/reset/verify-email screens, minimal authenticated home view with a bridge create-company form. See `docs/decisions-log.md` for the Tailwind monorepo `@source` gotcha found while verifying this. |
| **2a — Onboarding fields, Clients, app shell** ✅ | `Company.bank_account`/`uses_sef` + onboarding-completion endpoint, `apps.clients` domain (first real `TenantScopedManager` default-manager usage), `AppShell` nav, Clients list/create/edit screens, `currentCompany` store. See `docs/decisions-log.md`. |
| **2b — Invoice backend** ✅ | `Invoice`/`InvoiceLineItem`/`InvoiceSequence`/`FinancialEvent` models, race-safe server-side numbering, `InvoiceService` status state machine (draft→issued→cancelled), RBAC wired to the pre-existing `create_invoice`/`edit_invoice`/`cancel_invoice` codenames. Backend only — see `docs/decisions-log.md` (⚠️ numbering format unverified against real Serbian requirements). |
| **2c — Invoice creation UX** *(next)* | `apps/app` screens wired to the Phase 2b API: list, create/edit draft, detail (doubles as the pre-issue preview), issue/cancel actions. New `packages/ui` primitives as needed (`MoneyDisplay`, `Badge`) |
| **2d — Invoice PDF/email/payments/dashboard** | PDF template system, email sending, payment tracking, the real Dashboard (replaces `HomeView`'s placeholder) |
| **3 — Compliance** | KPO, Limits (+ rules engine + what-if calculator), Obligations, Notifications, Documents |
| **3 — Compliance** | KPO, Limits (+ rules engine + what-if calculator), Obligations, Notifications, Documents |
| **4 — Accounting platform** | Accounting organization, client relationships, accountant dashboard, permissions |
| **5 — Billing** | Trial, Subscriptions, Plans, Entitlements |
| **6 — QA** | Tests, security review, performance, responsive/mobile pass |
| **7 — Beta** | Seeded realistic environment, closed beta |

## Things that must NOT be guessed (flagged per §81/§82 — confirm before encoding as real rules)

- Exact current paušal limits (annual turnover limit, rolling-365-day threshold, growth-of-tax-base rule) and their effective dates for 2026 — must come from an authoritative source (current Zakon o porezu na dohodak građana / Uredba), not from the blueprint's example numbers (6,000,000 / 8,000,000 RSD are illustrative in the source docs, not verified). Rules engine will seed these as `approval_status = "unverified/placeholder"` until confirmed.
- SEF/eFaktura integration details (auth model, document formats, sandbox access) — seam only, no implementation until confirmed.
- Fiscalization (PURS/ESIR) requirements — architecture seam only.
- Final subscription pricing tiers and entitlement limits (ranges only exist today).
- Payment processor for subscription billing (RSD card processing / local PSP) — not chosen yet.
- Hosting/deployment target for staging/production — out of scope for local dev bootstrap; can be decided later without blocking Phase 1a/1b.

## Risks

- **Regulatory correctness**: biggest risk given this handles real tax-adjacent data — mitigated by the rules-engine + explicit "unverified" flag above, never silently treating placeholders as fact.
- **Scope**: the spec is large (SEF, fiscalization, banking, AI all mentioned) — master prompt itself warns against overbuilding (§78); this plan holds the MVP line and defers everything else to labeled V2/V3.
- **Two-person bandwidth vs. spec size**: sequencing (roadmap above) is designed so each phase produces a usable increment rather than a big-bang release.
- **Multi-tenant security**: cross-tenant data leaks are the classic SaaS failure mode — tenant-scoping tests are called out explicitly as a Phase 1b requirement, not deferred to Phase 6.

## What happens immediately after approval (Phase 1a execution)

1. `git init`, initial commit of the two canonical spec docs (`Pausalac.md`, `pausalac-blueprint.md`, untouched, current paths) + new `docs/` content. The redundant `pausalac-product-blueprint.md` and `pausalni_product_blueprint.docx` are moved (not deleted) into `docs/source/archive/` so nothing is lost, and are excluded from being treated as sources of truth going forward.
2. Create `docs/implementation-plan.md` + `docs/decisions-log.md` (this plan's content, adapted for the repo).
3. Scaffold the monorepo: `pnpm-workspace.yaml`, root `package.json`, `.gitignore`, `.editorconfig`, `.env.example`, `docker-compose.yml` (postgres/redis/minio/mailhog).
4. `apps/api`: Django project + DRF installed, settings split (`base/dev/staging/prod`), empty domain app skeletons (`accounts, companies, clients, invoices, payments, kpo, limits, taxes, documents, notifications, analytics, subscriptions, integrations, audit`), `/health` endpoint, Celery wiring (no tasks yet).
5. `apps/app`: Vue 3 + Vite + TS + Tailwind, configured with the blueprint's design tokens, empty shell.
6. `apps/web`: Nuxt 4 skeleton, same design tokens, empty landing page.
7. Root `README.md` with setup instructions for the colleague (clone, install, `docker compose up`, run migrations, run dev servers).
8. Minimal GitHub Actions CI (lint + build placeholders for both stacks).

**Explicitly not started yet**: auth, tenancy enforcement, RBAC, audit infra, any business domain logic — these become the next planned chunk (Phase 1b) once the skeleton is reviewed and running.

## Verification

- `docker compose up` brings up Postgres/Redis/MinIO/MailHog cleanly.
- `apps/api`: `python manage.py runserver` boots, `/health` returns 200, `python manage.py migrate` runs against the compose Postgres with zero app migrations (framework only).
- `apps/app` and `apps/web`: `pnpm dev` in each boots a blank page styled with the shared design tokens (verifies Tailwind config + palette wiring).
- `pnpm -w lint` / CI workflow runs green on the empty skeleton.
