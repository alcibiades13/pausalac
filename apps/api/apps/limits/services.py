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

from apps.invoices.ledger import monthly_issued_revenue, sum_issued_revenue
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
    def compute_pausal_limit_history(company, year: int, as_of: date | None = None) -> dict:
        """Monthly cumulative revenue toward the calendar-year paušal
        limit, plus a projected path to year-end for `LimitProgressChart`
        (blueprint §6.5). Shares its numbers with `compute_pausal_limit`
        rather than recomputing them separately: `monthly_issued_revenue`
        is the same ledger function `_build_tracker` calls (via
        `sum_issued_revenue`), and the projected year-end total is the
        exact same `_projection` linear-extrapolation the dashboard's
        text line already shows — this just spreads that one number
        across the remaining months as a path instead of stating it once.
        """
        as_of = as_of or date.today()
        period_start = date(year, 1, 1)
        period_end = date(year, 12, 31)
        is_current_year = period_start <= as_of <= period_end
        history_end = as_of if is_current_year else period_end

        history: list[dict] = []
        running = Decimal("0.00")
        for row in monthly_issued_revenue(company, period_start, history_end):
            running += row["amount"]
            history.append({"month": row["month"], "cumulative": running})

        rule = get_active_rule("pausal_turnover_limit", as_of)
        threshold = Decimal(str(rule.config["amount"]))
        currency = rule.config.get("currency", company.default_currency)

        projection: list[dict] = []
        if is_current_year:
            current_total = running  # last history point — computed from the same partial-month query, so the two lines meet exactly
            estimate = _projection(current_total, period_start, period_end, as_of)
            if estimate is not None:
                end_of_year_total = estimate["estimated_period_end"]
                remaining_months: list[str] = []
                cursor = date(as_of.year, as_of.month, 1)
                end_marker = date(period_end.year, period_end.month, 1)
                while cursor <= end_marker:
                    remaining_months.append(cursor.isoformat())
                    cursor = (
                        date(cursor.year + 1, 1, 1)
                        if cursor.month == 12
                        else date(cursor.year, cursor.month + 1, 1)
                    )
                steps = len(remaining_months) - 1
                for i, month in enumerate(remaining_months):
                    value = (
                        current_total
                        if steps == 0
                        else current_total
                        + (end_of_year_total - current_total) * Decimal(i) / Decimal(steps)
                    )
                    projection.append({"month": month, "cumulative": value.quantize(Decimal("0.01"))})

        return {
            "year": year,
            "threshold": threshold,
            "currency": currency,
            "history": history,
            "projection": projection,
        }

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
