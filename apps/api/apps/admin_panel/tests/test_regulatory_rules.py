from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry
from apps.limits.models import RegulatoryRule


class AdminRegulatoryRuleWorkflowTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email="super@pausalac.rs", password="s3cr3t-pass", is_staff=True, is_superuser=True
        )
        self.staff_user = User.objects.create_user(
            email="staff@pausalac.rs", password="s3cr3t-pass", is_staff=True
        )
        self.list_url = reverse("admin-rule-list", kwargs={"version": "v1"})

    def test_superuser_can_create_a_new_version(self):
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.list_url,
            {
                "identifier": "turnover_limit",
                "config": {"amount": "6000000", "currency": "RSD"},
                "effective_from": "2026-01-01",
                "source": "Zakon o porezu na dohodak građana",
                "version": 1,
                "notes": "",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        rule = RegulatoryRule.objects.get(identifier="turnover_limit")
        self.assertEqual(rule.approval_status, RegulatoryRule.ApprovalStatus.UNVERIFIED)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="regulatory_rule", entity_id=str(rule.id), action="admin_created"
            ).exists()
        )

    def test_staff_without_superuser_cannot_create(self):
        self.client.login(username="staff@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.list_url,
            {
                "identifier": "turnover_limit",
                "config": {},
                "effective_from": "2026-01-01",
                "source": "x",
                "version": 1,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_approve_flips_status_and_audit_logs_the_transition(self):
        rule = RegulatoryRule.objects.create(
            identifier="turnover_limit",
            config={"amount": "6000000", "currency": "RSD"},
            effective_from="2026-01-01",
            source="Zakon o porezu na dohodak građana",
        )
        approve_url = reverse("admin-rule-approve", kwargs={"version": "v1", "pk": rule.id})

        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, 200)
        rule.refresh_from_db()
        self.assertEqual(rule.approval_status, RegulatoryRule.ApprovalStatus.CONFIRMED)

        entry = AuditLogEntry.objects.get(
            entity_type="regulatory_rule", entity_id=str(rule.id), action="admin_approved"
        )
        self.assertEqual(entry.old_value["approval_status"], "unverified")
        self.assertEqual(entry.new_value["approval_status"], "confirmed")

    def test_staff_without_superuser_cannot_approve(self):
        rule = RegulatoryRule.objects.create(
            identifier="turnover_limit",
            config={},
            effective_from="2026-01-01",
            source="x",
        )
        approve_url = reverse("admin-rule-approve", kwargs={"version": "v1", "pk": rule.id})
        self.client.login(username="staff@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, 403)
        rule.refresh_from_db()
        self.assertEqual(rule.approval_status, RegulatoryRule.ApprovalStatus.UNVERIFIED)

    def test_edit_is_not_allowed_versions_are_additive_only(self):
        """The ViewSet only mixes in List+Create (no Retrieve/Update/
        Destroy), so DRF's router never generates a detail route at all —
        editing a version isn't just permission-denied, the URL doesn't
        exist."""
        rule = RegulatoryRule.objects.create(
            identifier="turnover_limit",
            config={},
            effective_from="2026-01-01",
            source="x",
        )
        detail_url = f"{self.list_url}{rule.id}/"
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        response = self.client.patch(
            detail_url, {"notes": "edited"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
