"""
Client-facing aggregations (master prompt §15/blueprint §6.3's client
profile: total invoiced, total paid, outstanding, invoice count, last
invoice). Computed server-side via DB aggregates rather than summed from
a paginated page of invoices client-side — §59 explicitly warns against
correctness-by-frontend-summing for anything meant to scale.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TypedDict

from django.db.models import Max, Sum

from apps.invoices.models import Invoice
from apps.payments.models import Payment

# Profaktura is non-binding (Phase 6c) and never contributes revenue —
# excluded from every total here, same as it's excluded from FinancialEvent/
# KPO/turnover-limit calculations. Draft/cancelled invoices never counted
# toward anything either (same "was it ever issued" discipline as the
# ledger — master prompt §97).
_COUNTED_STATUSES = [
    Invoice.Status.ISSUED,
    Invoice.Status.SENT,
    Invoice.Status.VIEWED,
    Invoice.Status.PARTIALLY_PAID,
    Invoice.Status.PAID,
    Invoice.Status.OVERDUE,
]


class ClientSummary(TypedDict):
    total_invoiced: Decimal
    total_paid: Decimal
    outstanding: Decimal
    invoice_count: int
    last_invoice_date: date | None


class ClientService:
    @staticmethod
    def compute_summary(client) -> ClientSummary:
        counted = Invoice.objects.filter(
            client=client,
            document_type__in=[Invoice.DocumentType.INVOICE, Invoice.DocumentType.ADVANCE],
            status__in=_COUNTED_STATUSES,
        )

        totals = counted.aggregate(total_invoiced=Sum("total"), last_invoice_date=Max("issue_date"))
        total_invoiced = totals["total_invoiced"] or Decimal("0.00")

        total_paid = Payment.objects.filter(invoice__client=client).aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")

        return ClientSummary(
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            outstanding=total_invoiced - total_paid,
            invoice_count=counted.count(),
            last_invoice_date=totals["last_invoice_date"],
        )
