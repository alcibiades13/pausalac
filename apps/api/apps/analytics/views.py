"""
Dashboard aggregation (master prompt §8) — the one place that reads across
Invoices/Payments/Companies to answer "how's my business doing" in one
call. Deliberately does NOT include Limits or Next-obligation sections:
those need the versioned rules engine (§25) and the Tax/Obligation domain
respectively, neither of which exist yet (Phase 3) — see
docs/decisions-log.md for the cash-vs-accrual flag this also inherits.
"""

from datetime import date
from decimal import Decimal

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.onboarding import compute_onboarding_status
from apps.companies.permissions import HasCompanyPermission
from apps.invoices.models import FinancialEvent, Invoice

OUTSTANDING_STATUSES = [
    Invoice.Status.ISSUED,
    Invoice.Status.SENT,
    Invoice.Status.PARTIALLY_PAID,
    Invoice.Status.OVERDUE,
]


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get(self, request, *args, **kwargs):
        company = request.company

        revenue = self._revenue_ytd(company)
        outstanding = self._outstanding(company)
        onboarding = compute_onboarding_status(company)

        attention = []
        if outstanding["overdue_count"]:
            attention.append(
                {
                    "type": "overdue_invoices",
                    "message": (
                        f"{outstanding['overdue_count']} faktura(e) kasni sa ukupno "
                        f"{outstanding['overdue_total']} {company.default_currency} potraživanja."
                    ),
                    "action": {"route": "invoices", "query": {"status": "overdue"}},
                }
            )
        if not request.user.is_email_verified:
            attention.append(
                {
                    "type": "email_unverified",
                    "message": "Potvrdi svoju email adresu da bi nalog bio potpuno aktivan.",
                    "action": {"route": "home"},
                }
            )
        if onboarding["missing"] and set(onboarding["missing"]) & {"company", "bank", "client"}:
            # sef/tax_document are permanently missing for now (see
            # compute_onboarding_status) — only the actionable items
            # belong in the attention center, not the two known gaps.
            attention.append(
                {
                    "type": "onboarding_incomplete",
                    "message": f"Tvoj nalog je {onboarding['percentage']}% podešen.",
                    "action": {"route": "settings"},
                }
            )

        if outstanding["overdue_count"]:
            business_health = {
                "status": "critical",
                "reasons": [f"{outstanding['overdue_count']} faktura(e) kasni sa naplatom."],
            }
        elif attention:
            business_health = {
                "status": "attention",
                "reasons": [item["message"] for item in attention],
            }
        else:
            business_health = {"status": "ok", "reasons": []}

        return Response(
            {
                "business_health": business_health,
                "attention": attention,
                "revenue": revenue,
                "outstanding": outstanding,
                "onboarding": onboarding,
            }
        )

    @staticmethod
    def _revenue_ytd(company) -> dict:
        year_start = date(timezone.now().year, 1, 1)
        events = FinancialEvent.objects.for_company(company).filter(
            event_type__in=[
                FinancialEvent.EventType.INVOICE_ISSUED,
                FinancialEvent.EventType.INVOICE_CANCELLED,
            ],
            occurred_at__date__gte=year_start,
        )
        issued = events.filter(event_type=FinancialEvent.EventType.INVOICE_ISSUED).aggregate(
            total=Coalesce(Sum("amount"), Value(Decimal("0.00")))
        )["total"]
        cancelled = events.filter(event_type=FinancialEvent.EventType.INVOICE_CANCELLED).aggregate(
            total=Coalesce(Sum("amount"), Value(Decimal("0.00")))
        )["total"]
        return {
            "ytd": issued - cancelled,
            "currency": company.default_currency,
            # Explicit so nothing downstream mistakes this for the (not yet
            # built) regulatory limit calculation, which may need to be
            # cash-basis instead — see docs/decisions-log.md.
            "basis": "invoiced",
        }

    @staticmethod
    def _outstanding(company) -> dict:
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

        return {
            "count": invoices.count(),
            "total": total,
            "currency": company.default_currency,
            "overdue_count": overdue_count,
            "overdue_total": overdue_total,
        }
