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
| **2c — Invoice creation UX** ✅ | `packages/ui`'s `MoneyDisplay`/`Badge`, `apps/app`'s invoice list (status filter)/create-edit form (dynamic line items)/detail-as-preview with issue/cancel, `InvoiceStatusBadge`. Small backend addition: paginated list endpoints now accept `?page_size=`. See `docs/decisions-log.md`. |
| **2d — Invoice PDF + email sending** ✅ | WeasyPrint-based PDF template system (`apps/invoices/pdf.py`), `GET /invoices/{id}/pdf/` (tenancy resolved from the invoice itself, not the usual header), `POST /invoices/{id}/send/` + Celery task, `ISSUED → SENT` transition (only after send succeeds). Frontend: download/send actions on `InvoiceDetailView`. See `docs/decisions-log.md`. |
| **2e — Payments + overdue detection** ✅ | New `apps.payments` domain (idempotent `PaymentService.record_payment`, top-level `/api/v1/payments/`), `PARTIALLY_PAID`/`PAID` derivation, Celery Beat overdue sweep (`InvoiceService.mark_overdue_all`) + management command, payment recording/history UX on `InvoiceDetailView`. ⚠️ Cash-vs-accrual limit-basis question flagged, not resolved — see `docs/decisions-log.md`. |
| **2f — Real Dashboard** ✅ | `apps.analytics.DashboardView` (business health + aggregated attention center + revenue YTD + outstanding-net-of-payments + onboarding bar), `compute_onboarding_status` extracted for shared use, `SettingsView` split off `HomeView` to keep the dashboard calm. Limits/Next-obligation sections deliberately deferred to Phase 3. See `docs/decisions-log.md`. |
| **3a — Rules engine + Limits** ✅ | `apps.limits.RegulatoryRule` (versioned, platform-wide, §25), seeded via data migration with the 2026-09-14 consultation's constants (all `approval_status="unverified"`); `LimitsService` (paušal turnover + VAT-registration trackers, warning tiers, year-end projection) + what-if calculator (`POST /limits/simulate/`, pure — no writes); `apps.invoices.ledger.sum_issued_revenue` extracted for shared use with the Dashboard; Dashboard now folds Limits into its attention center/business health. Frontend: `LimitTracker`, `/limiti` (nav + what-if UI), compact Limits card on the dashboard. See `docs/decisions-log.md`. |
| **3b — KPO** ✅ | `InvoiceLineItem.item_type` (service/product split), `apps.kpo.KPOEntry` auto-generated from `InvoiceService.issue`/`cancel` (storno rows on cancellation, never edited/deleted), `GET /kpo/` (date-range filter) + PDF/Excel export (own-id addressed, like invoice PDF), `KPOListView` + invoice-form line-item type picker (new `Select` primitive). See `docs/decisions-log.md` (⚠️ KPO numbering yearly-reset assumption unverified; ⚠️ Limits' revenue-date basis vs. KPO's flagged as a deferred inconsistency, not fixed this phase). |
| **3c — Obligations** ✅ | `apps.taxes.TaxResolution`/`TaxObligation` — resolution-driven monthly obligations (never rate-computed), due-date rolling for weekends, non-blocking `rate_check_warnings` against the Phase 3a `RegulatoryRule` table, overdue sweep (Celery Beat + management command, mirrors invoices'), `manage_tax_obligations` RBAC activated. Dashboard `next_obligation` section completed. Frontend: `ObligationsView`, dashboard card. Also: `AppShell` nav reworked to a mobile-first collapsible menu (user-flagged regression fix). See `docs/decisions-log.md` (⚠️ holiday calendar not accounted for; ⚠️ no resolution correction flow yet; ⚠️ payment-details copy deliberately not built). |
| **3d — Notifications** ✅ | `apps.notifications.Notification` (one row per recipient+channel), hooked into the existing `InvoiceService`/`TaxService` `mark_overdue_all` sweeps (`invoice_overdue`→attention/in-app, `tax_obligation_overdue`→critical/in-app+email), email delivery mirroring the invoice-send task pattern, `dedup_key`+unique-constraint backstop. Frontend: bell+badge in `AppShell`, `NotificationsView`. See `docs/decisions-log.md` (⚠️ push notifications, limit-tier-crossing notifications, and channel preferences all deliberately deferred). |
| **3e — Documents** ✅ | `apps.documents.Document` — the first real file upload/object-storage usage in the codebase (MinIO/S3, presigned `file_url`, delete removes the storage object too), scoped to `tax_resolution`/`contract`/`sef_document`/`fiscal_receipt`/`other` (invoice/KPO PDFs keep their own existing views, not duplicated here). Activates `view_documents`/`upload_documents` RBAC. Dashboard attention entry for `TaxResolution`s missing a linked document. Fixed two real setup gaps found while building this: no test-storage isolation (now `InMemoryStorage` in `config/settings/test.py`) and the MinIO bucket was never auto-created (`docker-compose.yml` now has a `minio-init` service). See `docs/decisions-log.md`. **Closes the "Phase 3 — Compliance" functional arc (3a–3e).** |
| **3f — Design & UX Overhaul** ✅ | "Ledger" direction — confident fintech look (layered shadows + a teal accent) chosen over literal glassmorphism for legibility/performance reasons on a trust-critical, mobile-first compliance tool; light mode only, dark mode deferred. New `--color-primary`/`--font-display`/`--font-mono` tokens, redesigned `packages/ui` primitives, new `Skeleton` primitive (replaced all 11 bare "Učitavanje..." states), `AppShell`/`AuthLayout` refresh, `font-mono` on invoice/KPO identifiers, row hover-highlights on clickable lists. Also fixed a real bug found while planning: Inter was declared but never actually loaded since Phase 1c. See `docs/decisions-log.md` (visual result not browser-verified by Claude — no screenshot tool in this environment — user should review `pnpm dev` at both desktop and mobile widths before considering this done). **Closes the visual-identity phase; Phase 4 starts on the new baseline.** |
| **4a — Accounting organizations & client connections** ✅ | New `apps.accounting` domain: `AccountingOrganization`/`AccountingOrganizationMembership` (admin/staff), `AccountingConnection` (company↔org, append-only history), `SyncedMembership`. An active connection provisions real `apps.companies.Membership` rows for org staff (reusing the `accountant`/`accountant_admin` roles that have sat unused since Phase 1b) — zero changes needed to the existing RBAC/tenant-scoping stack. Org invites client by PIB, client OWNER accepts/declines via the existing notifications domain (3d). Frontend: real company switcher (`AppShell`, closes a Phase 2a gap), `AccountingView` ("Moj računovođa"), `AccountingOrganizationView` (org/staff/client management, linked from Settings). See `docs/decisions-log.md` (⚠️ messaging/§32 and the full accountant dashboard/§28-§29 deliberately deferred to 4b; a real `http_method_names`/DELETE routing bug was found via live-stack E2E testing and fixed, with the missing view-level test coverage added). |
| **4b — Accountant dashboard** *(next)* | Aggregated cross-client accountant "command center" (§28/§29, blueprint §13): client-portfolio table (status/revenue/limits/obligations/documents), bulk visibility across every connected company. Needs 4a's real multi-company access to exist first. |
| **5 — Billing** | Trial, Subscriptions, Plans, Entitlements |
| **6 — QA** | Tests, security review, performance, responsive/mobile pass |
| **7 — Beta** | Seeded realistic environment, closed beta |

## Things that must NOT be guessed (flagged per §81/§82 — confirm before encoding as real rules)

- Paušal limit (6,000,000 RSD, calendar year, promet-based — not bank receipts), VAT-registration threshold (8,000,000 RSD, trailing 12 consecutive months — a *separate* tracker from the paušal limit, never merged with it), and the 2026/2027 tax-base growth cap (paušalna poreska osnovica capped at +10% year-over-year, per a late-2025 Uredba amendment) — refined from one vague flag into three distinct constants per the 2026-09-14 consultation (see `docs/decisions-log.md`), but still not cross-checked here against a primary source (Zakon o porezu na dohodak građana / Uredba o paušalnom oporezivanju) or a licensed računovođa. Rules engine will seed these as `approval_status = "unverified/placeholder"` until that final confirmation happens.
- KPO obrazac's exact column structure (redni broj poslovne promene / datum i opis knjiženja / prihod od prodaje proizvoda / prihod od izvršenih usluga / svega prihodi, income-only — no expense columns) and the monthly, resolution-driven tax-obligation model (rates stored as reference data only; actual owed amounts come from a user-entered "poresko rešenje", not computed by the app) — both modeled per the same 2026-09-14 consultation, same pending-confirmation caveat as above.
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
