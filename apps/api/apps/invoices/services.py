"""
Invoice business logic (master prompt §112 names InvoiceService
explicitly) — views stay thin, all state-changing logic lives here.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.audit.services import AuditService

from .models import FinancialEvent, Invoice, InvoiceLineItem
from .numbering import assign_invoice_number
from .pdf import format_money

Status = Invoice.Status
DocumentType = Invoice.DocumentType

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

        # Profaktura is a non-binding quote (Phase 6c, docs/decisions-log.md)
        # — no revenue is ever recognized for it, so it must never create a
        # FinancialEvent/KPOEntry. Avans is deliberately NOT excluded here:
        # user-confirmed it behaves exactly like a real invoice for ledger/
        # turnover-limit purposes.
        if invoice.document_type != Invoice.DocumentType.PROFORMA:
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

        if was_ever_issued and invoice.document_type != Invoice.DocumentType.PROFORMA:
            # A cancelled draft never counted toward anything — only
            # reverse the ledger impact of an invoice that was actually
            # issued (master prompt §97: inclusion/exclusion must be explicit).
            # Profaktura never created a FinancialEvent/KPOEntry in issue()
            # above, so there's nothing to reverse here either.
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

        track_event("invoice_sent", user=actor, company=invoice.company, invoice_id=invoice.id)
        return invoice

    @staticmethod
    def mark_overdue_all() -> int:
        """
        System-triggered bulk sweep (master prompt §61: "overdue checks" as
        a named background job) — called from
        apps.invoices.tasks.mark_overdue_invoices_task (Celery Beat) and
        the `check_overdue_invoices` management command, never duplicated
        between the two. No FinancialEvent: this is a status/timestamp
        change only, not a cash or revenue event. Profaktura is excluded —
        a non-binding quote doesn't "go overdue" in any meaningful sense
        (Phase 6c); Avans stays included, same as a regular invoice.
        """
        candidates = (
            Invoice.objects.select_related("client", "company")
            .filter(status__in=OVERDUE_ELIGIBLE_STATUSES, due_date__lt=timezone.now().date())
            .exclude(document_type=Invoice.DocumentType.PROFORMA)
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

            # Client-facing payment reminder (master prompt §107) —
            # distinct from the internal notification above, which goes
            # to the paušalac, not the client. This is the exact gap
            # docs/decisions-log.md's Phase 6 audit flagged as missing.
            if invoice.client.email:
                from apps.notifications.email import EmailService  # lazy — see above

                EmailService.send(
                    "payment_reminder",
                    {
                        "invoice_number": invoice.invoice_number,
                        "company_name": invoice.company.name,
                        "total_formatted": format_money(invoice.total),
                        "currency": invoice.currency,
                        "due_date": invoice.due_date.strftime("%d.%m.%Y."),
                    },
                    to=[invoice.client.email],
                    subject=f"Podsetnik: faktura {invoice.invoice_number} kasni",
                )
            count += 1
        return count

    @staticmethod
    @transaction.atomic
    def convert_to_invoice(profaktura: Invoice, actor) -> Invoice:
        """
        Turns an issued/sent Profaktura into a real, independent draft
        Invoice (Phase 6c) — never a settlement/netting mechanism, just a
        one-time copy. The Profaktura itself is untouched (still ISSUED/
        SENT, a historical document, not consumed) other than gaining a
        reverse `conversions` row. Allowed only once per Profaktura — the
        conversions.exists() check — to stop duplicate real invoices from
        being created by mistake; the caller is expected to show the
        already-converted invoice instead of the action once this fires.
        """
        if profaktura.document_type != DocumentType.PROFORMA:
            raise InvalidTransitionError("Samo profaktura može da se konvertuje u fakturu.")
        if profaktura.status not in (Status.ISSUED, Status.SENT):
            raise InvalidTransitionError(
                "Profaktura mora biti izdata da bi se konvertovala u fakturu."
            )
        if profaktura.conversions.exists():
            raise InvalidTransitionError("Ova profaktura je već konvertovana u fakturu.")

        line_items = [
            {
                "description": item.description,
                "item_type": item.item_type,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in profaktura.items.all()
        ]
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=profaktura.company,
            client=profaktura.client,
            line_items=line_items,
            currency=profaktura.currency,
            issue_date=today,
            due_date=today + timedelta(days=15),
            service_date=today,
            notes=profaktura.notes,
            document_type=DocumentType.INVOICE,
            converted_from=profaktura,
        )
        AuditService.log(
            actor=actor,
            company=profaktura.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="converted_from_profaktura",
            old_value={"profaktura_id": profaktura.id},
            new_value={"invoice_id": invoice.id},
        )
        return invoice

    @staticmethod
    @transaction.atomic
    def duplicate_invoice(source: Invoice, actor) -> Invoice:
        """
        Master prompt §94: "When previous invoice exists: allow
        duplication." Available from any source status (unlike
        convert_to_invoice, which is issued/sent-only) — duplicating is a
        one-time copy, not a tracked relationship, so unlike conversion
        there's no linkage field and no "only once" restriction. Preserves
        the source's own document_type (duplicating a Profaktura produces
        a new Profaktura draft, not a type change — that's convert's job).
        """
        line_items = [
            {
                "description": item.description,
                "item_type": item.item_type,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in source.items.all()
        ]
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=source.company,
            client=source.client,
            line_items=line_items,
            currency=source.currency,
            issue_date=today,
            due_date=today + timedelta(days=15),
            service_date=today,
            notes=source.notes,
            document_type=source.document_type,
        )
        AuditService.log(
            actor=actor,
            company=source.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="duplicated_from",
            old_value={"source_invoice_id": source.id},
            new_value={"invoice_id": invoice.id},
        )
        return invoice
