from datetime import date

from django.test import TestCase

from apps.limits.models import RegulatoryRule
from apps.limits.rules import get_active_rule


class GetActiveRuleTests(TestCase):
    def test_exact_effective_from_boundary_matches(self):
        rule = RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "1.00"},
            effective_from=date(2026, 1, 1),
            source="test",
        )
        self.assertEqual(get_active_rule("test_rule", date(2026, 1, 1)), rule)

    def test_before_effective_from_does_not_match(self):
        RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "1.00"},
            effective_from=date(2026, 1, 1),
            source="test",
        )
        with self.assertRaises(RegulatoryRule.DoesNotExist):
            get_active_rule("test_rule", date(2025, 12, 31))

    def test_effective_until_boundary(self):
        rule = RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "1.00"},
            effective_from=date(2026, 1, 1),
            effective_until=date(2027, 12, 31),
            source="test",
        )
        self.assertEqual(get_active_rule("test_rule", date(2027, 12, 31)), rule)
        with self.assertRaises(RegulatoryRule.DoesNotExist):
            get_active_rule("test_rule", date(2028, 1, 1))

    def test_no_expiry_matches_indefinitely(self):
        rule = RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "1.00"},
            effective_from=date(2026, 1, 1),
            source="test",
        )
        self.assertEqual(get_active_rule("test_rule", date(2099, 1, 1)), rule)

    def test_highest_version_wins_on_tie(self):
        RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "1.00"},
            effective_from=date(2026, 1, 1),
            source="test",
            version=1,
        )
        latest = RegulatoryRule.objects.create(
            identifier="test_rule",
            config={"amount": "2.00"},
            effective_from=date(2026, 1, 1),
            source="test",
            version=2,
        )
        self.assertEqual(get_active_rule("test_rule", date(2026, 6, 1)), latest)
