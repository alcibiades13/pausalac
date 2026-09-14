from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.notifications.models import Notification


class NotificationViewSetTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.list_url = reverse("notification-list", kwargs={"version": "v1"})

        self.in_app = Notification.objects.create(
            company=self.company,
            recipient=self.owner,
            event_type="invoice_overdue",
            dedup_key="k1",
            priority=Notification.Priority.ATTENTION,
            channel=Notification.Channel.IN_APP,
            title="Faktura kasni",
            message="M",
        )
        Notification.objects.create(
            company=self.company,
            recipient=self.owner,
            event_type="tax_obligation_overdue",
            dedup_key="k2",
            priority=Notification.Priority.CRITICAL,
            channel=Notification.Channel.EMAIL,
            title="Poreska obaveza kasni",
            message="M",
        )

    def test_list_only_returns_in_app_rows(self):
        response = self.client.get(self.list_url, **self.headers)
        body = response.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["results"][0]["event_type"], "invoice_overdue")

    def test_is_read_filter(self):
        response = self.client.get(self.list_url, {"is_read": "false"}, **self.headers)
        self.assertEqual(response.json()["count"], 1)
        response = self.client.get(self.list_url, {"is_read": "true"}, **self.headers)
        self.assertEqual(response.json()["count"], 0)

    def test_mark_read(self):
        url = reverse("notification-mark-read", kwargs={"version": "v1", "pk": self.in_app.id})
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json()["read_at"])
        self.in_app.refresh_from_db()
        self.assertIsNotNone(self.in_app.read_at)

    def test_cannot_mark_another_users_notification_read(self):
        other_user = User.objects.create_user(email="other@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=other_user, company=self.company)
        self.client.logout()
        self.client.login(username="other@pausalac.rs", password="s3cr3t-pass")
        url = reverse("notification-mark-read", kwargs={"version": "v1", "pk": self.in_app.id})
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        Membership.objects.create(user=self.owner, company=other_company)
        response = self.client.get(self.list_url, HTTP_X_COMPANY_ID=str(other_company.id))
        self.assertEqual(response.json()["count"], 0)
