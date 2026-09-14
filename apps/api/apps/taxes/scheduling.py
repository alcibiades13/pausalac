"""
Due-date calculation for monthly tax/contribution obligations. Per the
2026-09-14 regulatory consultation: due the 15th of the month following
the reporting month, rolled to the next business day if the 15th falls
on a non-workday.

WEEKENDS ONLY — Serbian public holidays are NOT accounted for. A
maintained holiday calendar needs a real, confirmed source; guessing at
one would be worse than not having it. Flagged in docs/decisions-log.md.
"""

from datetime import date, timedelta

SATURDAY = 5
SUNDAY = 6


def next_due_date(period_start: date) -> date:
    if period_start.month == 12:
        due_month_year, due_month = period_start.year + 1, 1
    else:
        due_month_year, due_month = period_start.year, period_start.month + 1
    due = date(due_month_year, due_month, 15)
    if due.weekday() == SATURDAY:
        due += timedelta(days=2)
    elif due.weekday() == SUNDAY:
        due += timedelta(days=1)
    return due
