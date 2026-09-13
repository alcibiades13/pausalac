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

# Only the transitions reachable this phase. SENT/VIEWED/PARTIALLY_PAID/
# PAID/OVERDUE join this map in 2c/2d once email, tracking, and payments
# exist to drive them — the enum and DB constraint already allow for it
# (apps/invoices/models.py), only this map and its callers grow then.
TRANSITIONS: dict[str, set[str]] = {
    Status.DRAFT: {Status.ISSUED, Status.CANCELLED},
    Status.ISSUED: {Status.CANCELLED},
    Status.CANCELLED: set(),
}


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

        was_issued = invoice.status == Status.ISSUED
        old_status = invoice.status
        invoice.status = Status.CANCELLED
        invoice.cancelled_at = timezone.now()
        invoice.save(update_fields=["status", "cancelled_at", "updated_at"])

        if was_issued:
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
