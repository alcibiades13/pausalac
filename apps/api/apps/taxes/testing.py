"""
Test-only fixture helper — same reasoning as apps.limits.testing: tests
must not depend on the data migration's seeded RegulatoryRule rows being
present at arbitrary points in a test run (see docs/decisions-log.md,
Phase 3a's serialized_rollback fix).
"""

from datetime import date

from apps.limits.models import RegulatoryRule

RATES = {
    "income_tax_rate": "0.1000",
    "pio_rate": "0.2400",
    "health_rate": "0.1030",
    "unemployment_rate": "0.0075",
}


def seed_test_rates() -> None:
    for identifier, rate in RATES.items():
        RegulatoryRule.objects.create(
            identifier=identifier,
            config={"rate": rate},
            effective_from=date(2020, 1, 1),
            source="test fixture",
        )
