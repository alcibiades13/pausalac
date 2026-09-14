"""
Accountant client-portfolio aggregation (master prompt §28/§29, blueprint
§13, Phase 4b). The one place in the app with a genuine N+1 risk — an
organization can have on the order of §60's own example scale (126
clients) — so every figure here is computed with a small, fixed number of
queries across the *whole* portfolio at once, never one query per client.
See docs/decisions-log.md for the full query-budget breakdown.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce

from apps.invoices.models import FinancialEvent, Invoice
from apps.limits.models import RegulatoryRule
from apps.limits.rules import get_active_rule
from apps.limits.services import LimitsService
from apps.taxes.models import TaxObligation, TaxResolution

from .models import AccountingConnection


def _grouped_revenue(company_ids: list[int], start: date, end: date) -> dict[int, Decimal]:
    """Issued-minus-cancelled revenue per company for [start, end], in the
    same two queries `apps.invoices.ledger.sum_issued_revenue` would run
    per company — just grouped across every company at once instead."""
    rows = (
        FinancialEvent.objects.filter(
            company_id__in=company_ids,
            event_type__in=[
                FinancialEvent.EventType.INVOICE_ISSUED,
                FinancialEvent.EventType.INVOICE_CANCELLED,
            ],
            occurred_at__date__gte=start,
            occurred_at__date__lte=end,
        )
        .values("company_id", "event_type")
        .annotate(total=Coalesce(Sum("amount"), Value(Decimal("0.00"))))
    )
    revenue: dict[int, Decimal] = dict.fromkeys(company_ids, Decimal("0.00"))
    for row in rows:
        sign = 1 if row["event_type"] == FinancialEvent.EventType.INVOICE_ISSUED else -1
        revenue[row["company_id"]] = revenue.get(row["company_id"], Decimal("0.00")) + (
            sign * row["total"]
        )
    return revenue


def _next_obligations(company_ids: list[int]) -> dict[int, TaxObligation]:
    """Earliest pending/overdue obligation per company — one query across
    every company, mirrors DashboardView._next_obligation's own filter and
    ordering exactly, picked per-company in Python."""
    obligations = TaxObligation.objects.filter(
        company_id__in=company_ids,
        status__in=[TaxObligation.Status.PENDING, TaxObligation.Status.OVERDUE],
    ).order_by("company_id", "due_date")
    next_by_company: dict[int, TaxObligation] = {}
    for obligation in obligations:
        next_by_company.setdefault(obligation.company_id, obligation)
    return next_by_company


def _counts_by_company(queryset, company_ids: list[int]) -> dict[int, int]:
    rows = queryset.filter(company_id__in=company_ids).values("company_id").annotate(
        count=Count("id")
    )
    counts = dict.fromkeys(company_ids, 0)
    counts.update({row["company_id"]: row["count"] for row in rows})
    return counts


def _client_status(
    *,
    overdue_invoice_count: int,
    pausal_warning_level: str | None,
    vat_warning_level: str | None,
    next_obligation_overdue: bool,
    missing_document_count: int,
) -> str:
    """Mirrors DashboardView.business_health's real escalation logic,
    restricted to the drivers §29's column list actually asks for —
    deliberately excludes the onboarding/email-verification nudges
    DashboardView also folds in, since those are personal-account prompts
    for the client, not portfolio-relevant signals for their accountant."""
    critical_drivers = (
        overdue_invoice_count > 0
        or pausal_warning_level == "critical"
        or vat_warning_level == "critical"
        or next_obligation_overdue
    )
    if critical_drivers:
        return "critical"
    attention_drivers = (
        pausal_warning_level in ("attention", "warning")
        or vat_warning_level in ("attention", "warning")
        or missing_document_count > 0
    )
    if attention_drivers:
        return "attention"
    return "ok"


def compute_client_portfolio(organization) -> list[dict]:
    connections = list(
        AccountingConnection.objects.filter(
            organization=organization, status=AccountingConnection.Status.ACTIVE
        ).select_related("company")
    )
    if not connections:
        return []

    company_ids = [c.company_id for c in connections]
    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)
    trailing_start = today - timedelta(days=365)

    pausal_revenue = _grouped_revenue(company_ids, year_start, year_end)
    vat_revenue = _grouped_revenue(company_ids, trailing_start, today)

    try:
        pausal_rule = get_active_rule("pausal_turnover_limit", today)
        pausal_threshold = Decimal(str(pausal_rule.config["amount"]))
    except RegulatoryRule.DoesNotExist:
        pausal_threshold = None
    try:
        vat_rule = get_active_rule("vat_registration_threshold", today)
        vat_threshold = Decimal(str(vat_rule.config["amount"]))
    except RegulatoryRule.DoesNotExist:
        vat_threshold = None

    next_obligations = _next_obligations(company_ids)
    overdue_invoice_counts = _counts_by_company(
        Invoice.objects.filter(status=Invoice.Status.OVERDUE), company_ids
    )
    # `documents__isnull` traverses apps.documents.Document.tax_resolution's
    # related_name — same query DashboardView runs per company, just
    # grouped across every company here.
    missing_document_counts = _counts_by_company(
        TaxResolution.objects.filter(documents__isnull=True), company_ids
    )

    portfolio = []
    for connection in connections:
        company = connection.company
        pausal_current = pausal_revenue.get(company.id, Decimal("0.00"))
        vat_current = vat_revenue.get(company.id, Decimal("0.00"))
        pausal = (
            LimitsService.summarize(pausal_current, pausal_threshold)
            if pausal_threshold is not None
            else {"percentage": None, "warning_level": None}
        )
        vat = (
            LimitsService.summarize(vat_current, vat_threshold)
            if vat_threshold is not None
            else {"percentage": None, "warning_level": None}
        )
        next_obligation = next_obligations.get(company.id)
        next_obligation_overdue = (
            next_obligation is not None and next_obligation.status == TaxObligation.Status.OVERDUE
        )
        overdue_invoice_count = overdue_invoice_counts.get(company.id, 0)
        missing_document_count = missing_document_counts.get(company.id, 0)

        portfolio.append(
            {
                "company_id": company.id,
                "company_name": company.name,
                "company_pib": company.pib,
                "granted_role": connection.granted_role,
                "status": _client_status(
                    overdue_invoice_count=overdue_invoice_count,
                    pausal_warning_level=pausal["warning_level"],
                    vat_warning_level=vat["warning_level"],
                    next_obligation_overdue=next_obligation_overdue,
                    missing_document_count=missing_document_count,
                ),
                "revenue_ytd": pausal_current,
                "currency": company.default_currency,
                "pausal_limit": pausal,
                "vat_threshold": vat,
                "next_obligation_due": (
                    next_obligation.due_date.isoformat() if next_obligation else None
                ),
                "next_obligation_overdue": next_obligation_overdue,
                "overdue_invoice_count": overdue_invoice_count,
                "missing_document_count": missing_document_count,
                "integration_errors": None,
            }
        )
    return portfolio


def summarize_portfolio(portfolio: list[dict]) -> dict:
    summary = {"total": len(portfolio), "ok": 0, "attention": 0, "critical": 0}
    for row in portfolio:
        summary[row["status"]] += 1
    return summary
