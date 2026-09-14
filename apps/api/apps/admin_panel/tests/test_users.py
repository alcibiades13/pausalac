from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry


class AdminUserDeactivateReactivateTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email="super@pausalac.rs", password="s3cr3t-pass", is_staff=True, is_superuser=True
        )
        self.staff_user = User.objects.create_user(
            email="staff@pausalac.rs", password="s3cr3t-pass", is_staff=True
        )
        self.target = User.objects.create_user(email="target@pausalac.rs", password="s3cr3t-pass")
        self.deactivate_url = reverse(
            "admin-user-deactivate", kwargs={"version": "v1", "pk": self.target.id}
        )
        self.reactivate_url = reverse(
            "admin-user-reactivate", kwargs={"version": "v1", "pk": self.target.id}
        )

    def test_superuser_can_deactivate_and_reactivate(self):
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")

        response = self.client.post(self.deactivate_url)
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="user", entity_id=str(self.target.id), action="admin_deactivated"
            ).exists()
        )

        response = self.client.post(self.reactivate_url)
        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_active)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="user", entity_id=str(self.target.id), action="admin_reactivated"
            ).exists()
        )

    def test_staff_without_superuser_cannot_deactivate(self):
        self.client.login(username="staff@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(self.deactivate_url)
        self.assertEqual(response.status_code, 403)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_active)

    def test_deactivated_user_is_blocked_from_logging_in(self):
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        self.client.post(self.deactivate_url)
        self.client.logout()
        logged_in = self.client.login(username="target@pausalac.rs", password="s3cr3t-pass")
        self.assertFalse(logged_in)
