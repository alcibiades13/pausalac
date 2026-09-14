"""
Payment business logic (master prompt §112: explicit service layer). All
state-changing work — including the resulting Invoice status update —
happens here, atomically, so a Payment row and its Invoice-status/ledger
side effects are never created out of sync with each other.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit.services import AuditService
from apps.invoices.models import FinancialEvent, Invoice
from apps.invoices.services import PAYABLE_STATUSES

from .models import Payment


class InvalidPaymentError(Exception):
    """Raised for anything that makes a payment ineligible — views turn this into a 400."""


class PaymentService:
    @staticmethod
    @transaction.atomic
    def record_payment(
        invoice: Invoice,
        *,
        amount: Decimal,
        paid_at,
        method: str,
        notes: str,
        actor,
        idempotency_key: str = "",
    ) -> Payment:
        if idempotency_key:
            existing = Payment.objects.filter(
                company=invoice.company, idempotency_key=idempotency_key
            ).first()
            if existing is not None:
                # Replay of an already-processed request (master prompt
                # §62's literal "clicks Mark as paid twice" case) — return
                # what already happened instead of processing it again.
                return existing

        if invoice.status not in PAYABLE_STATUSES:
            raise InvalidPaymentError(
                f"Faktura u statusu '{invoice.status}' ne može da primi uplatu."
            )
        if amount <= 0:
            raise InvalidPaymentError("Iznos uplate mora biti veći od nule.")

        payment = Payment.objects.create(
            company=invoice.company,
            invoice=invoice,
            amount=amount,
            currency=invoice.currency,
            paid_at=paid_at,
            method=method,
            notes=notes,
            idempotency_key=idempotency_key,
        )

        total_paid = invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        old_status = invoice.status
        if total_paid >= invoice.total:
            invoice.status = Invoice.Status.PAID
            invoice.paid_at = timezone.now()
            invoice.save(update_fields=["status", "paid_at", "updated_at"])
            event_type = FinancialEvent.EventType.INVOICE_PAID
        else:
            invoice.status = Invoice.Status.PARTIALLY_PAID
            invoice.save(update_fields=["status", "updated_at"])
            event_type = FinancialEvent.EventType.INVOICE_PARTIALLY_PAID

        # This payment's own amount, not the invoice total or the running
        # total — summing every payment-type event for an invoice must
        # reconstruct exactly what was received (see docs/decisions-log.md
        # on cash- vs. accrual-basis limit calculations, still unconfirmed).
        FinancialEvent.objects.create(
            company=invoice.company,
            invoice=invoice,
            event_type=event_type,
            amount=payment.amount,
            currency=payment.currency,
        )
        AuditService.log(
            actor=actor,
            company=invoice.company,
            entity_type="invoice",
            entity_id=invoice.id,
            action="payment_recorded",
            old_value={"status": old_status},
            new_value={"status": invoice.status, "payment_id": payment.id, "amount": str(amount)},
        )
        if invoice.status == Invoice.Status.PAID:
            # Lazy import — apps.analytics sits after apps.payments in
            # DOMAIN_APPS. Only the final "fully paid" transition is
            # "invoice_paid" (master prompt §73) — a partial payment isn't.
            from apps.analytics.tracking import track_event

            track_event("invoice_paid", user=actor, company=invoice.company, invoice_id=invoice.id)
        return payment
