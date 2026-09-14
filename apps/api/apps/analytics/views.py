"""
Dashboard aggregation (master prompt §8) — the one place that reads across
Invoices/Payments/Companies/Limits/Taxes to answer "how's my business
doing" in one call.
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
from apps.invoices.ledger import sum_issued_revenue
from apps.invoices.models import Invoice
from apps.limits.services import LimitsService
from apps.taxes.models import TaxObligation

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
        limits = LimitsService.compute_all(company)
        next_obligation = self._next_obligation(company)

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
        limit_labels = {"pausal_limit": "Paušalni limit", "vat_threshold": "PDV prag"}
        limits_critical = []
        limits_warning = []
        for key, label in limit_labels.items():
            tracker = limits[key]
            if tracker["warning_level"] == "critical":
                limits_critical.append((label, tracker))
            elif tracker["warning_level"] == "warning":
                limits_warning.append((label, tracker))
        for label, tracker in limits_critical + limits_warning:
            attention.append(
                {
                    "type": "limit_warning",
                    "message": (
                        f"{label} je na {tracker['percentage']}% (preostalo "
                        f"{tracker['remaining']} {tracker['currency']})."
                    ),
                    "action": {"route": "limits"},
                }
            )

        obligation_overdue = next_obligation is not None and next_obligation["status"] == "overdue"
        if obligation_overdue:
            attention.append(
                {
                    "type": "tax_obligation_overdue",
                    "message": (
                        f"Poreska obaveza za {next_obligation['period_start']} kasni "
                        f"({next_obligation['total_amount']} {company.default_currency})."
                    ),
                    "action": {"route": "obligations"},
                }
            )

        if outstanding["overdue_count"] or limits_critical or obligation_overdue:
            reasons = []
            if outstanding["overdue_count"]:
                reasons.append(f"{outstanding['overdue_count']} faktura(e) kasni sa naplatom.")
            reasons.extend(
                f"{label} je na {tracker['percentage']}%." for label, tracker in limits_critical
            )
            if obligation_overdue:
                reasons.append("Poreska obaveza kasni.")
            business_health = {"status": "critical", "reasons": reasons}
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
                "limits": limits,
                "next_obligation": next_obligation,
            }
        )

    @staticmethod
    def _revenue_ytd(company) -> dict:
        today = timezone.now().date()
        year_start = date(today.year, 1, 1)
        year_end = date(today.year, 12, 31)
        ytd = sum_issued_revenue(company, year_start, year_end)
        return {
            "ytd": ytd,
            "currency": company.default_currency,
            # Explicit so nothing downstream mistakes this for a Limits
            # figure, even though both now share the same promet/accrual
            # basis and the same sum_issued_revenue helper.
            "basis": "invoiced",
        }

    @staticmethod
    def _next_obligation(company) -> dict | None:
        obligation = (
            TaxObligation.objects.for_company(company)
            .filter(status__in=[TaxObligation.Status.PENDING, TaxObligation.Status.OVERDUE])
            .order_by("due_date")
            .first()
        )
        if obligation is None:
            return None
        return {
            "period_start": obligation.period_start.isoformat(),
            "due_date": obligation.due_date.isoformat(),
            "total_amount": obligation.total_amount,
            "currency": company.default_currency,
            "status": obligation.status,
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
