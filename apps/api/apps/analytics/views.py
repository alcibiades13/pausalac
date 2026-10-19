"""
Dashboard aggregation (master prompt §8) — the one place that reads across
Invoices/Payments/Companies/Limits/Taxes to answer "how's my business
doing" in one call.
"""

from datetime import date

from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.onboarding import compute_onboarding_status
from apps.companies.permissions import HasCompanyPermission
from apps.invoices.ledger import monthly_issued_revenue, outstanding_summary, sum_issued_revenue
from apps.limits.services import LimitsService
from apps.taxes.models import TaxObligation, TaxResolution
from config.pluralize import pluralize_sr


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get(self, request, *args, **kwargs):
        company = request.company

        revenue = self._revenue_ytd(company)
        outstanding = self._outstanding(company)
        onboarding = compute_onboarding_status(company)
        limits = LimitsService.compute_all(company)
        next_obligation = self._next_obligation(company)
        overdue_obligation = self._overdue_obligation(company)

        overdue_invoices_phrase = pluralize_sr(
            outstanding["overdue_count"], "faktura kasni", "fakture kasne", "faktura kasni"
        )

        attention = []
        if outstanding["overdue_count"]:
            attention.append(
                {
                    "type": "overdue_invoices",
                    "message": (
                        f"{outstanding['overdue_count']} {overdue_invoices_phrase} sa ukupno "
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
        missing_document_count = (
            TaxResolution.objects.for_company(company).filter(documents__isnull=True).count()
        )
        if missing_document_count:
            missing_document_phrase = pluralize_sr(
                missing_document_count,
                "poresko rešenje nema",
                "poreska rešenja nemaju",
                "poreskih rešenja nema",
            )
            attention.append(
                {
                    "type": "tax_resolution_missing_document",
                    "message": (
                        f"{missing_document_count} {missing_document_phrase} priložen dokument."
                    ),
                    "action": {"route": "documents"},
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

        obligation_overdue = overdue_obligation is not None
        if obligation_overdue:
            attention.append(
                {
                    "type": "tax_obligation_overdue",
                    "message": (
                        f"Poreska obaveza za {overdue_obligation['period_start']} kasni "
                        f"({overdue_obligation['total_amount']} {company.default_currency})."
                    ),
                    "action": {"route": "obligations"},
                }
            )

        # Lazy import — apps.subscriptions sits after apps.analytics in
        # DOMAIN_APPS (same precedent as every other lower-domain-calls-
        # later-domain case in this codebase).
        from apps.subscriptions.models import Subscription

        subscription = getattr(company, "subscription", None)
        subscription_inactive = subscription is not None and subscription.status in (
            Subscription.Status.EXPIRED,
            Subscription.Status.CANCELLED,
        )
        if subscription_inactive:
            attention.append(
                {
                    "type": "subscription_inactive",
                    "message": (
                        "Pretplata nije aktivna — izaberi plan da nastaviš da izdaješ fakture."
                    ),
                    "action": {"route": "subscription"},
                }
            )
        elif subscription is not None and subscription.status == Subscription.Status.TRIALING:
            days_left = (subscription.trial_ends_at.date() - timezone.now().date()).days
            if days_left <= 3:
                days_word = pluralize_sr(days_left, "dan", "dana", "dana")
                attention.append(
                    {
                        "type": "trial_ending_soon",
                        "message": f"Probni period ističe za {days_left} {days_word}.",
                        "action": {"route": "subscription"},
                    }
                )

        is_critical = (
            outstanding["overdue_count"]
            or limits_critical
            or obligation_overdue
            or subscription_inactive
        )
        if is_critical:
            reasons = []
            if outstanding["overdue_count"]:
                reasons.append(
                    f"{outstanding['overdue_count']} {overdue_invoices_phrase} sa naplatom."
                )
            reasons.extend(
                f"{label} je na {tracker['percentage']}%." for label, tracker in limits_critical
            )
            if obligation_overdue:
                reasons.append("Poreska obaveza kasni.")
            if subscription_inactive:
                reasons.append("Pretplata nije aktivna.")
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
            # For RevenueTrendChart — same monthly_issued_revenue function
            # LimitProgressChart's history reads, so the dashboard chart
            # and the limits chart never compute "revenue per month" two
            # different ways.
            "monthly_series": monthly_issued_revenue(company, year_start, year_end),
        }

    @staticmethod
    def _next_obligation(company) -> dict | None:
        """The genuinely upcoming obligation — PENDING only. An OVERDUE
        one is never "next" (it's already late), and surfaces instead via
        `_overdue_obligation`/the `tax_obligation_overdue` attention item —
        showing the same overdue row in both places read as a bug (two
        "sources of truth" disagreeing about what "next" means), found via
        an actual rendered dashboard, not assumed."""
        obligation = (
            TaxObligation.objects.for_company(company)
            .filter(status=TaxObligation.Status.PENDING)
            # `id` as a tie-breaker: two obligations can share a due_date
            # (nothing prevents it), and `order_by("due_date")` alone
            # would leave the choice between them up to the database's
            # own unspecified tie order — deterministic every time this
            # runs, but not guaranteed identical run to run.
            .order_by("due_date", "id")
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
    def _overdue_obligation(company) -> dict | None:
        obligation = (
            TaxObligation.objects.for_company(company)
            .filter(status=TaxObligation.Status.OVERDUE)
            .order_by("due_date", "id")
            .first()
        )
        if obligation is None:
            return None
        return {
            "period_start": obligation.period_start.isoformat(),
            "total_amount": obligation.total_amount,
        }

    @staticmethod
    def _outstanding(company) -> dict:
        return outstanding_summary(company)
