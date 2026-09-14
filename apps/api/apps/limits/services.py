"""
Limits computation (master prompt §17/§18, blueprint §6.5) and the
what-if calculator (§19/§98). Two genuinely separate trackers — never
merged into one bar, per the 2026-09-14 regulatory consultation
(docs/decisions-log.md): a calendar-year paušal turnover limit and a
trailing-12-months VAT-registration threshold. Both read the same
promet/accrual-basis revenue figure (apps.invoices.ledger.sum_issued_revenue)
the Dashboard's own revenue-YTD card uses.
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from apps.invoices.ledger import sum_issued_revenue
from apps.limits.rules import get_active_rule

MIN_DAYS_FOR_PROJECTION = 7


def _percentage(current: Decimal, threshold: Decimal) -> int:
    if threshold == 0:
        return 0
    return int((current / threshold * 100).to_integral_value(rounding=ROUND_HALF_UP))


def _warning_level(percentage: int) -> str:
    if percentage >= 95:
        return "critical"
    if percentage >= 85:
        return "warning"
    if percentage >= 70:
        return "attention"
    return "ok"


def _projection(current: Decimal, period_start: date, period_end: date, as_of: date) -> dict | None:
    """Linear extrapolation to the end of the period — only meaningful
    for a period with a real future end date (the calendar-year paušal
    limit), not the ever-sliding trailing-12-months VAT window."""
    days_elapsed = (as_of - period_start).days + 1
    if days_elapsed < MIN_DAYS_FOR_PROJECTION:
        return None
    total_days = (period_end - period_start).days + 1
    estimated = (current / days_elapsed * total_days).quantize(Decimal("0.01"))
    return {"estimated_period_end": estimated, "label": "procena"}


def _build_tracker(
    *,
    identifier: str,
    period_type: str,
    period_start: date,
    period_end: date,
    company,
    as_of: date,
    include_projection: bool,
) -> dict:
    rule = get_active_rule(identifier, as_of)
    threshold = Decimal(str(rule.config["amount"]))
    currency = rule.config.get("currency", company.default_currency)
    current = sum_issued_revenue(company, period_start, period_end)
    percentage = _percentage(current, threshold)
    return {
        "identifier": identifier,
        "period": {
            "type": period_type,
            "start": period_start.isoformat(),
            "end": period_end.isoformat(),
        },
        "threshold": threshold,
        "current": current,
        "currency": currency,
        "percentage": percentage,
        "remaining": threshold - current,
        "warning_level": _warning_level(percentage),
        "projection": _projection(current, period_start, period_end, as_of)
        if include_projection
        else None,
        "approval_status": rule.approval_status,
    }


class LimitsService:
    @staticmethod
    def summarize(current: Decimal, threshold: Decimal) -> dict:
        """Percentage/warning-tier math only — no query. Lets other
        aggregations (apps.accounting.dashboard's cross-client portfolio)
        reuse the exact same tiering logic as `_build_tracker` without a
        second copy of the rounding/threshold rules."""
        percentage = _percentage(current, threshold)
        return {"percentage": percentage, "warning_level": _warning_level(percentage)}

    @staticmethod
    def compute_pausal_limit(company, as_of: date | None = None) -> dict:
        as_of = as_of or date.today()
        period_start = date(as_of.year, 1, 1)
        period_end = date(as_of.year, 12, 31)
        return _build_tracker(
            identifier="pausal_turnover_limit",
            period_type="calendar_year",
            period_start=period_start,
            period_end=period_end,
            company=company,
            as_of=as_of,
            include_projection=True,
        )

    @staticmethod
    def compute_vat_threshold(company, as_of: date | None = None) -> dict:
        as_of = as_of or date.today()
        period_start = as_of - timedelta(days=365)
        return _build_tracker(
            identifier="vat_registration_threshold",
            period_type="trailing_12_months",
            period_start=period_start,
            period_end=as_of,
            company=company,
            as_of=as_of,
            include_projection=False,
        )

    @staticmethod
    def compute_all(company, as_of: date | None = None) -> dict:
        as_of = as_of or date.today()
        return {
            "pausal_limit": LimitsService.compute_pausal_limit(company, as_of),
            "vat_threshold": LimitsService.compute_vat_threshold(company, as_of),
        }

    @staticmethod
    def simulate(company, hypothetical_amount: Decimal, as_of: date | None = None) -> dict:
        """Pure calculation (§98) — no FinancialEvent/Invoice row is ever
        created here. `as_of` always falls inside both trackers' periods
        (a calendar year containing today, and a trailing window ending
        today), so the hypothetical amount is added to both."""
        as_of = as_of or date.today()
        before = LimitsService.compute_all(company, as_of)
        after = {}
        for key, tracker in before.items():
            threshold = tracker["threshold"]
            current = tracker["current"] + hypothetical_amount
            percentage = _percentage(current, threshold)
            after[key] = {
                **tracker,
                "current": current,
                "percentage": percentage,
                "remaining": threshold - current,
                "warning_level": _warning_level(percentage),
                "projection": None,
            }
        return {"before": before, "after": after}
