"""
Proves the read/write permission split (is_staff for reads, is_superuser
for writes) on two representative endpoints rather than repeating the
same check across all ten — the split is implemented once, in shared
code (AdminListView / get_permissions overrides), so one solid proof per
pattern is enough.
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.subscriptions.models import Plan


class AdminReadWritePermissionTests(TestCase):
    def setUp(self):
        self.plain_user = User.objects.create_user(
            email="plain@pausalac.rs", password="s3cr3t-pass"
        )
        self.staff_user = User.objects.create_user(
            email="staff@pausalac.rs", password="s3cr3t-pass", is_staff=True
        )
        self.superuser = User.objects.create_user(
            email="super@pausalac.rs", password="s3cr3t-pass", is_staff=True, is_superuser=True
        )
        self.plan = Plan.objects.create(identifier="starter", name="Starter", price="1500.00")
        self.users_url = reverse("admin-user-list", kwargs={"version": "v1"})
        self.plan_list_url = reverse("admin-plan-list", kwargs={"version": "v1"})
        self.plan_detail_url = reverse(
            "admin-plan-detail", kwargs={"version": "v1", "pk": self.plan.id}
        )

    def test_plain_user_is_forbidden_from_read_and_write(self):
        self.client.login(username="plain@pausalac.rs", password="s3cr3t-pass")
        self.assertEqual(self.client.get(self.users_url).status_code, 403)
        self.assertEqual(
            self.client.patch(
                self.plan_detail_url, {"price": "2000.00"}, content_type="application/json"
            ).status_code,
            403,
        )

    def test_staff_without_superuser_can_read_but_not_write(self):
        self.client.login(username="staff@pausalac.rs", password="s3cr3t-pass")
        self.assertEqual(self.client.get(self.users_url).status_code, 200)
        self.assertEqual(self.client.get(self.plan_list_url).status_code, 200)
        response = self.client.patch(
            self.plan_detail_url, {"price": "2000.00"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_read_and_write(self):
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        self.assertEqual(self.client.get(self.users_url).status_code, 200)
        response = self.client.patch(
            self.plan_detail_url, {"price": "2000.00"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.plan.refresh_from_db()
        self.assertEqual(str(self.plan.price), "2000.00")

    def test_unauthenticated_is_forbidden(self):
        self.assertEqual(self.client.get(self.users_url).status_code, 403)
