"""
Test-only fixture helper — same reasoning as apps.limits.testing's
seed_test_rules(): tests must not depend on migration-seeded Plan rows
being present at arbitrary points in a --reuse-db test run.
"""

from .models import Plan


def seed_test_plans() -> dict[str, Plan]:
    return {
        "starter": Plan.objects.create(identifier="starter", name="Starter", price="1500.00"),
        "professional": Plan.objects.create(
            identifier="professional", name="Professional", price="2000.00"
        ),
        "business": Plan.objects.create(identifier="business", name="Business", price="3000.00"),
    }
