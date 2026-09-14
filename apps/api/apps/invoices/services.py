"""
Invoice business logic (master prompt §112 names InvoiceService
explicitly) — views stay thin, all state-changing logic lives here.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.services import AuditService

from .models import FinancialEvent, Invoice, InvoiceLineItem
from .numbering import assign_invoice_number

Status = Invoice.Status

# VIEWED joins this once view-tracking exists to drive it. A sent (or
# overdue) invoice can still be cancelled — voiding something the client
# already received, or that just hasn't been paid by its due date, is a
# normal real-world case, same as an issued-but-not-yet-sent one.
# PARTIALLY_PAID/PAID have no entry here on purpose: once money is
# attached to an invoice, voiding it needs a refund/correction concept
# (master prompt §96 explicitly defers this) — not silently allowed.
TRANSITIONS: dict[str, set[str]] = {
    Status.DRAFT: {Status.ISSUED, Status.CANCELLED},
    Status.ISSUED: {Status.CANCELLED, Status.SENT},
    Status.SENT: {Status.CANCELLED},
    Status.OVERDUE: {Status.CANCELLED},
    Status.CANCELLED: set(),
}

# Statuses a payment can be recorded against (apps.payments.services).
# Distinct from TRANSITIONS above because the resulting status (PARTIALLY_
# PAID vs. PAID) is computed from the payment amount, not a fixed target —
# this is just the eligibility check, not a transition map entry.
PAYABLE_STATUSES: set[str] = {Status.ISSUED, Status.SENT, Status.PARTIALLY_PAID, Status.OVERDUE}

# Statuses the overdue sweep (mark_overdue_all) will flip once due_date
# has passed. PARTIALLY_PAID is included — master prompt §11's flat status
# enum has no combined "overdue-and-partially-paid" state; a partial
# payment already on the invoice is preserved (only status/timestamps
# change), a new payment afterward resolves it via PAYABLE_STATUSES above.
OVERDUE_ELIGIBLE_STATUSES: set[str] = {Status.ISSUED, Status.SENT, Status.PARTIALLY_PAID}


class InvalidTransitionError(Exception):
    """Raised for any status change not in TRANSITIONS — views turn this into a 400."""


def _line_items_total(line_items: list[dict]) -> Decimal:
    return sum(
        (Decimal(li["quantity"]) * Decimal(li["unit_price"]) for li in line_items), Decimal("0.00")
    )


class InvoiceService:
    @staticmethod
    @transaction.atomic
    def create_draft(*, company, client, line_items: list[dict], **fields) -> Invoice:
        currency = fields.pop("currency", None) or company.default_currency
        invoice = Invoice.objects.create(
            company=company,
            client=client,
            currency=currency,
            total=_line_items_total(line_items),
            **fields,
        )
        InvoiceService._replace_line_items(invoice, line_items)
        return invoice

    @staticmethod
    @transaction.atomic
    def update_draft(
        invoice: Invoice, *, line_items: list[dict] | None = None, **fields
    ) -> Invoice:
        if invoice.status != Status.DRAFT:
            raise InvalidTransitionError("Samo nacrt fakture može da se menja.")

        for key, value in fields.items():
            setattr(invoice, key, value)

        if line_items is not None:
            invoice.items.all().delete()
            InvoiceService._replace_line_items(invoice, line_items)
            invoice.total = _line_items_total(line_items)

        invoice.save()
        return invoice

    @staticmethod
    def _replace_line_items(invoice: Invoice, line_items: list[dict]) -> None:
        InvoiceLineItem.objects.bulk_create(
            [
                InvoiceLineItem(
                    invoice=invoice,
                    description=li["description"],
                    item_type=li.get("item_type", InvoiceLineItem.ItemType.SERVICE),
                    quantity=li["quantity"],
                    unit_price=li["unit_price"],
                    line_total=Decimal(li["quantity"]) * Decimal(li["unit_price"]),
                    position=index,
                )
                for index, li in enumerate(line_items)
            ]
        )

    @staticmethod
    @transaction.atomic
    def issue(invoice: Invoice, actor) -> Invoice:
        if Status.ISSUED not in TRANSITIONS.get(invoice.status, set()):
            raise InvalidTransitionError(
                f"Faktura u statusu '{invoice.status}' ne može da se izda."
            )
        if not invoice.items.exists():
            raise InvalidTransitionError("Faktura mora imati bar jednu stavku da bi bila izdata.")

        old_status = invoice.status
        invoice.invoice_number = assign_invoice_number(invoice)
        invoice.status = Status.ISSUED
        invoice.issued_at = timezone.now()
        invoice.save(update_fields=["invoice_number", "status", "issued_at", "updated_at"])

        FinancialEvent.objects.create(
            company=invoice.company,
            invoice=invoice,
            event_type=FinancialEvent.EventType.INVOICE_ISSUED,
            amount=invoice.total,
            currency=invoice.currency,
        )
        # Lazy import: apps.kpo depends on apps.invoices (domain-list
        # order), so a module-level import the other way would invert
        # that direction. Deliberate, contained exception — same pattern
        # as CompanyViewSet.onboarding's lazy Client import (Phase 2a).
        from apps.kpo.services import KPOService

        KPOService.record_issued(invoice)
        AuditService.log(
            actor=actor,
            company=invoice.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="issued",
            old_value={"status": old_status},
            new_value={"status": invoice.status, "invoice_number": invoice.invoice_number},
        )
        return invoice

    @staticmethod
    @transaction.atomic
    def cancel(invoice: Invoice, actor) -> Invoice:
        if Status.CANCELLED not in TRANSITIONS.get(invoice.status, set()):
            raise InvalidTransitionError(
                f"Faktura u statusu '{invoice.status}' ne može da se stornira."
            )

        # Whether revenue was ever recognized for this invoice — true for
        # ISSUED and anything downstream of it (SENT, ...), not just the
        # literal current status, so cancelling a *sent* invoice still
        # reverses the original issue event correctly.
        was_ever_issued = invoice.issued_at is not None
        old_status = invoice.status
        invoice.status = Status.CANCELLED
        invoice.cancelled_at = timezone.now()
        invoice.save(update_fields=["status", "cancelled_at", "updated_at"])

        if was_ever_issued:
            # A cancelled draft never counted toward anything — only
            # reverse the ledger impact of an invoice that was actually
            # issued (master prompt §97: inclusion/exclusion must be explicit).
            FinancialEvent.objects.create(
                company=invoice.company,
                invoice=invoice,
                event_type=FinancialEvent.EventType.INVOICE_CANCELLED,
                amount=invoice.total,
                currency=invoice.currency,
            )
            from apps.kpo.services import KPOService  # lazy — see issue() above

            KPOService.record_cancelled(invoice)
        AuditService.log(
            actor=actor,
            company=invoice.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="cancelled",
            old_value={"status": old_status},
            new_value={"status": invoice.status},
        )
        return invoice

    @staticmethod
    @transaction.atomic
    def mark_sent(invoice: Invoice, actor) -> Invoice:
        """
        Called from apps.invoices.tasks.send_invoice_email_task only after
        the email actually sends — never eagerly from the view — so the
        status can never claim "sent" for something delivery failed on.
        No FinancialEvent: sending doesn't change revenue (Phase 2b's
        ledger-is-revenue-only decision), so this is audit-trail-only,
        the same treatment INVOICE_CREATED got.
        """
        if Status.SENT not in TRANSITIONS.get(invoice.status, set()):
            raise InvalidTransitionError(
                f"Faktura u statusu '{invoice.status}' ne može da se označi kao poslata."
            )

        old_status = invoice.status
        invoice.status = Status.SENT
        invoice.sent_at = timezone.now()
        invoice.save(update_fields=["status", "sent_at", "updated_at"])

        AuditService.log(
            actor=actor,
            company=invoice.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="sent",
            old_value={"status": old_status},
            new_value={"status": invoice.status},
        )
        # Lazy import — apps.analytics sits after apps.invoices in DOMAIN_APPS.
        from apps.analytics.tracking import track_event

        track_event(
            "invoice_sent", user=actor, company=invoice.company, invoice_id=invoice.id
        )
        return invoice

    @staticmethod
    def mark_overdue_all() -> int:
        """
        System-triggered bulk sweep (master prompt §61: "overdue checks" as
        a named background job) — called from
        apps.invoices.tasks.mark_overdue_invoices_task (Celery Beat) and
        the `check_overdue_invoices` management command, never duplicated
        between the two. No FinancialEvent: this is a status/timestamp
        change only, not a cash or revenue event.
        """
        candidates = Invoice.objects.filter(
            status__in=OVERDUE_ELIGIBLE_STATUSES, due_date__lt=timezone.now().date()
        )
        count = 0
        for invoice in candidates:
            old_status = invoice.status
            invoice.status = Status.OVERDUE
            invoice.save(update_fields=["status", "updated_at"])
            AuditService.log(
                actor=None,
                company=invoice.company,
                entity_type="invoice",
                entity_id=invoice.id,
                action="marked_overdue",
                old_value={"status": old_status},
                new_value={"status": invoice.status},
                source="celery",
            )
            # Lazy import: notifications sits after invoices in the domain
            # list, so a module-level import the other way would invert
            # that direction — same documented exception as the kpo hook
            # in InvoiceService.issue/cancel.
            from apps.notifications.models import Notification
            from apps.notifications.services import NotificationService

            NotificationService.notify_company(
                invoice.company,
                event_type="invoice_overdue",
                dedup_key=f"invoice_overdue:{invoice.id}",
                priority=Notification.Priority.ATTENTION,
                title="Faktura kasni",
                message=(
                    f"Faktura {invoice.invoice_number} kasni "
                    f"{(timezone.now().date() - invoice.due_date).days} dana."
                ),
                action_route="invoices",
                action_query={"status": "overdue"},
            )
            from apps.analytics.tracking import track_event  # lazy — see above

            track_event("invoice_overdue", company=invoice.company, invoice_id=invoice.id)
            count += 1
        return count
