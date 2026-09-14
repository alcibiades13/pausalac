"""
Test-only fixture helper. Tests must not depend on the data migration's
RegulatoryRule rows being present at arbitrary points in a test run: an
unrelated TransactionTestCase elsewhere in the suite (e.g.
apps.invoices.tests.test_numbering) flushes every table after itself,
and a plain TestCase running afterward sees whatever is left on disk —
not what the migration originally seeded. Explicit fixtures make Limits/
Dashboard tests self-contained instead of order-dependent.
"""

from datetime import date

from apps.limits.models import RegulatoryRule


def seed_test_rules() -> None:
    RegulatoryRule.objects.create(
        identifier="pausal_turnover_limit",
        config={"amount": "6000000.00", "currency": "RSD", "period": "calendar_year"},
        effective_from=date(2020, 1, 1),
        source="test fixture",
    )
    RegulatoryRule.objects.create(
        identifier="vat_registration_threshold",
        config={"amount": "8000000.00", "currency": "RSD", "period": "trailing_12_months"},
        effective_from=date(2020, 1, 1),
        source="test fixture",
    )
