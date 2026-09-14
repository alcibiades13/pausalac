from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry
from apps.subscriptions.models import Plan


class AdminPlanCrudTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email="super@pausalac.rs", password="s3cr3t-pass", is_staff=True, is_superuser=True
        )
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        self.list_url = reverse("admin-plan-list", kwargs={"version": "v1"})

    def test_create_plan_is_audit_logged(self):
        response = self.client.post(
            self.list_url,
            {
                "identifier": "pro",
                "name": "Professional",
                "price": "2000.00",
                "currency": "RSD",
                "billing_interval": "monthly",
                "entitlements": {},
                "is_active": True,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        plan = Plan.objects.get(identifier="pro")
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="plan", entity_id=str(plan.id), action="admin_created"
            ).exists()
        )

    def test_update_plan_price_is_audit_logged_with_old_and_new_value(self):
        plan = Plan.objects.create(identifier="starter", name="Starter", price="1500.00")
        detail_url = reverse("admin-plan-detail", kwargs={"version": "v1", "pk": plan.id})

        response = self.client.patch(
            detail_url, {"price": "1800.00"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        plan.refresh_from_db()
        self.assertEqual(str(plan.price), "1800.00")

        entry = AuditLogEntry.objects.get(
            entity_type="plan", entity_id=str(plan.id), action="admin_updated"
        )
        self.assertEqual(entry.old_value["price"], "1500.00")
        self.assertEqual(entry.new_value["price"], "1800.00")

    def test_delete_is_not_allowed(self):
        plan = Plan.objects.create(identifier="starter", name="Starter", price="1500.00")
        detail_url = reverse("admin-plan-detail", kwargs={"version": "v1", "pk": plan.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 405)
