"""
Shared "issued revenue over a period" computation (master prompt §21's
ledger, read side). Both the Dashboard's revenue-YTD figure and the
Limits trackers (Phase 3a) need this exact sum — extracted so the two
never drift into computing it two different ways, same discipline as
apps.companies.onboarding.compute_onboarding_status.
"""

from datetime import date
from decimal import Decimal

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from apps.invoices.models import FinancialEvent


def sum_issued_revenue(company, start: date, end: date) -> Decimal:
    """Sum of INVOICE_ISSUED minus INVOICE_CANCELLED FinancialEvents whose
    occurred_at date falls within [start, end] inclusive. Promet/accrual
    basis, not cash — see docs/decisions-log.md (2026-09-14 entry)."""
    events = FinancialEvent.objects.for_company(company).filter(
        event_type__in=[
            FinancialEvent.EventType.INVOICE_ISSUED,
            FinancialEvent.EventType.INVOICE_CANCELLED,
        ],
        occurred_at__date__gte=start,
        occurred_at__date__lte=end,
    )
    issued = events.filter(event_type=FinancialEvent.EventType.INVOICE_ISSUED).aggregate(
        total=Coalesce(Sum("amount"), Value(Decimal("0.00")))
    )["total"]
    cancelled = events.filter(event_type=FinancialEvent.EventType.INVOICE_CANCELLED).aggregate(
        total=Coalesce(Sum("amount"), Value(Decimal("0.00")))
    )["total"]
    return issued - cancelled
