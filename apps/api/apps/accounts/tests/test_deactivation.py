"""
Self-service account deactivation (master prompt §106). See
docs/data-retention.md for the policy this implements.
"""

from django.test import TestCase
from django.urls import reverse

from apps.audit.models import AuditLogEntry
from apps.companies.models import Company, Membership

from ..models import User


class DeactivateAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="111222333")
        Membership.objects.create(user=self.user, company=self.company)
        self.client.login(username="marko@pausalac.rs", password="s3cr3t-pass")
        self.url = reverse("auth-deactivate", kwargs={"version": "v1"})

    def test_deactivation_sets_is_active_false_and_logs_out(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 204)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # Session ended — a follow-up authenticated call now fails.
        me_response = self.client.get(reverse("auth-me", kwargs={"version": "v1"}))
        self.assertEqual(me_response.status_code, 403)

    def test_deactivation_is_audit_logged(self):
        self.client.post(self.url)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="user", entity_id=self.user.id, action="deactivated"
            ).exists()
        )

    def test_deactivated_user_cannot_log_back_in(self):
        self.client.post(self.url)
        self.client.logout()
        response = self.client.post(
            reverse("auth-login", kwargs={"version": "v1"}),
            {"email": "marko@pausalac.rs", "password": "s3cr3t-pass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_deactivation_leaves_owned_data_untouched(self):
        self.client.post(self.url)
        # Master prompt §106: no arbitrary destructive deletion — the
        # company and membership the user owned still exist exactly as
        # they were.
        self.assertTrue(Company.objects.filter(id=self.company.id).exists())
        self.assertTrue(
            Membership.objects.filter(user=self.user, company=self.company).exists()
        )

    def test_requires_authentication(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
