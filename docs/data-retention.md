# Data retention policy

Written for master prompt §106 (DATA RETENTION), which requires a defined
policy for deleted accounts, cancelled subscriptions, invoices, documents,
and audit logs, and explicitly forbids "arbitrary destructive deletion."

## What this document does and doesn't cover

This defines the **mechanism** (what actually happens in the system when
an account is deactivated, a subscription is cancelled, etc.) and states
it honestly where a number is genuinely missing. It does **not** invent
specific retention **periods** (e.g. "financial records are kept for N
years") — Serbian tax/accounting law almost certainly specifies real
numbers here, and per this project's standing rule (master prompt §81/82,
see `docs/decisions-log.md`), a legal fact like that is never guessed.
Every "TBD" below is a real gap to close with a confirmed source before
this product handles real customer data in production, not a placeholder
nobody intends to revisit.

## Account deactivation

- **Mechanism**: `POST /api/v1/auth/deactivate/` (self-service, the only
  entry point today) sets `User.is_active = False` and ends the session.
  This is enforced by Django's own authentication backend — an inactive
  user cannot log back in — with no extra code needed.
- **What happens to their data**: nothing. Companies, memberships,
  invoices, KPO entries, documents, tax obligations, and audit log
  entries the user's account touched are left completely untouched. A
  company with other active members keeps functioning normally; a
  company whose only member deactivates becomes inaccessible (no one can
  log in to reach it) but its data is not deleted.
- **Reactivation**: deliberately not self-service this phase — it needs
  an operator action. The natural home for this is Phase 6b's in-app
  admin panel (not built yet); until then, reactivation is a manual
  database/Django-admin operation.
- **Hard deletion**: not implemented, and not planned until a real
  retention period is confirmed (see below) — deleting a user row today
  would either cascade-delete or orphan real financial records, which
  is exactly the "arbitrary destructive deletion" §106 forbids.

## Cancelled subscriptions

`Subscription.status = "cancelled"` (`apps.subscriptions`, Phase 5) is
itself the retained record — cancelling never deletes the `Subscription`
row, `Plan` history, or any `AuditLogEntry` describing it. There is no
separate cleanup job and none is planned.

## Invoices, KPO entries, tax obligations, documents

All of these are already append-only or soft-delete by construction, from
the phases that built them (see `docs/decisions-log.md`):

- Invoices are never hard-deleted — cancellation is a status transition
  (`Invoice.Status.CANCELLED`), not a row removal.
- `FinancialEvent`/`KPOEntry` rows are never edited or deleted; a
  cancellation produces an offsetting event instead.
- `Document` deletion (`DocumentService.delete`) does remove the row and
  its object-storage file — the one genuinely destructive operation in
  the system today, and it's a direct, explicit user action (a user
  deleting their own uploaded file), not a retention-driven sweep.
- Tax obligations/resolutions are immutable once created.

**TBD, not invented**: how long invoices/KPO/tax records must be kept
after a company stops using the product or is deactivated. This is a
real Serbian accounting/tax-law question (financial-record retention
periods), not an engineering decision — flagged here rather than guessed,
same discipline as every other unconfirmed regulatory number in this
project (see the RegulatoryRule `approval_status="unverified"` rows in
`apps.limits`/`apps.taxes`).

## Audit logs

`AuditLogEntry` rows (`apps.audit`) are append-only and never deleted by
any code path today. No retention period is defined — audit logs
accumulate indefinitely until a real policy (and, likely, a real legal
minimum retention period) is confirmed.

## Summary table

| Data | Deleted on account deactivation? | Hard-delete mechanism exists? | Retention period |
|---|---|---|---|
| User account | No (soft: `is_active=False`) | No | N/A |
| Company / Membership | No | No | N/A |
| Invoices / FinancialEvent / KPOEntry | No | No | **TBD** — unconfirmed legal minimum |
| Tax resolutions / obligations | No | No | **TBD** — unconfirmed legal minimum |
| Documents | No | Yes, user-initiated only (`DocumentService.delete`) | User-controlled |
| Subscriptions | No | No | N/A |
| Audit log entries | No | No | **TBD** |
