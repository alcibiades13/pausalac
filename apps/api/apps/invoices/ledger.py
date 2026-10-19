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
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from apps.invoices.models import FinancialEvent, Invoice

OUTSTANDING_STATUSES = [
    Invoice.Status.ISSUED,
    Invoice.Status.SENT,
    Invoice.Status.PARTIALLY_PAID,
    Invoice.Status.OVERDUE,
]


def monthly_issued_revenue(company, start: date, end: date) -> list[dict]:
    """Same issued-minus-cancelled figure `sum_issued_revenue` computes,
    grouped by month instead of summed over the whole range — the one
    source both `RevenueTrendChart` and `LimitProgressChart` read, so
    neither can silently drift from the other or from the existing
    YTD/limit totals that already use `sum_issued_revenue`. Always
    returns one row per calendar month in [start, end], even months with
    no activity at all (amount "0.00") — a chart needs a stable X-axis,
    not a queryset that skips silent months.
    """
    events = FinancialEvent.objects.for_company(company).filter(
        event_type__in=[
            FinancialEvent.EventType.INVOICE_ISSUED,
            FinancialEvent.EventType.INVOICE_CANCELLED,
        ],
        occurred_at__date__gte=start,
        occurred_at__date__lte=end,
    )
    rows = (
        events.annotate(month=TruncMonth("occurred_at"))
        .values("month", "event_type")
        .annotate(total=Coalesce(Sum("amount"), Value(Decimal("0.00"))))
    )
    by_month: dict[str, Decimal] = {}
    for row in rows:
        key = row["month"].date().replace(day=1).isoformat()
        sign = 1 if row["event_type"] == FinancialEvent.EventType.INVOICE_ISSUED else -1
        by_month[key] = by_month.get(key, Decimal("0.00")) + (sign * row["total"])

    months: list[dict] = []
    cursor = date(start.year, start.month, 1)
    end_marker = date(end.year, end.month, 1)
    while cursor <= end_marker:
        key = cursor.isoformat()
        months.append({"month": key, "amount": by_month.get(key, Decimal("0.00"))})
        cursor = date(cursor.year + 1, 1, 1) if cursor.month == 12 else date(cursor.year, cursor.month + 1, 1)
    return months


def outstanding_summary(company) -> dict:
    """Live snapshot (not period-scoped) of what's still owed, plus the
    YTD-paid figure `InvoiceStatusBreakdown` needs alongside it — the
    exact computation `DashboardView._outstanding` already did, moved
    here so a dedicated, lighter invoices endpoint can reuse it without
    the whole Dashboard payload, and so there is exactly one place this
    math lives rather than two call sites drifting apart."""
    invoices = (
        Invoice.objects.for_company(company)
        .filter(status__in=OUTSTANDING_STATUSES)
        .annotate(paid_amount=Coalesce(Sum("payments__amount"), Value(Decimal("0.00"))))
    )

    total = Decimal("0.00")
    overdue_total = Decimal("0.00")
    overdue_count = 0
    for invoice in invoices:
        remaining = invoice.total - invoice.paid_amount
        total += remaining
        if invoice.status == Invoice.Status.OVERDUE:
            overdue_total += remaining
            overdue_count += 1

    today = timezone.now().date()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)
    paid_ytd = (
        Invoice.objects.for_company(company)
        .filter(status=Invoice.Status.PAID, issue_date__gte=year_start, issue_date__lte=year_end)
        .aggregate(total=Coalesce(Sum("total"), Value(Decimal("0.00"))))["total"]
    )

    return {
        "count": invoices.count(),
        "total": total,
        "currency": company.default_currency,
        "overdue_count": overdue_count,
        "overdue_total": overdue_total,
        "paid_ytd": paid_ytd,
    }


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
