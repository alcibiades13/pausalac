from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company, Membership

from ..models import Subscription
from ..services import SubscriptionService
from ..testing import seed_test_plans


class PlanListViewTests(TestCase):
    def setUp(self):
        self.plans = seed_test_plans()
        self.user = User.objects.create_user(email="user@pausalac.rs", password="s3cr3t-pass")

    def test_authenticated_user_sees_active_plans(self):
        self.client.login(username="user@pausalac.rs", password="s3cr3t-pass")
        url = reverse("subscription-plans", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        identifiers = {plan["identifier"] for plan in response.json()}
        self.assertEqual(identifiers, {"starter", "professional", "business"})

    def test_requires_authentication(self):
        url = reverse("subscription-plans", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_inactive_plan_excluded(self):
        self.plans["starter"].is_active = False
        self.plans["starter"].save(update_fields=["is_active"])
        self.client.login(username="user@pausalac.rs", password="s3cr3t-pass")
        url = reverse("subscription-plans", kwargs={"version": "v1"})
        response = self.client.get(url)
        identifiers = {plan["identifier"] for plan in response.json()}
        self.assertNotIn("starter", identifiers)


class SubscriptionViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123123123")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("subscription-current", kwargs={"version": "v1"})

    def test_provisions_a_trial_on_first_read(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "trialing")
        self.assertIsNone(body["plan"])
        self.assertTrue(
            Subscription.objects.filter(company=self.company, status="trialing").exists()
        )

    def test_any_active_member_can_read(self):
        accountant = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)


class ActivatePlanViewTests(TestCase):
    def setUp(self):
        self.plans = seed_test_plans()
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="321321321")
        Membership.objects.create(user=self.owner, company=self.company)
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("subscription-activate", kwargs={"version": "v1"})

    def test_owner_can_activate_a_plan(self):
        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.url,
            {"plan": self.plans["professional"].id},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "active")
        self.assertEqual(body["plan"]["identifier"], "professional")

    def test_accountant_cannot_activate(self):
        accountant = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.url,
            {"plan": self.plans["professional"].id},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 403)


class CancelSubscriptionViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="654654654")
        Membership.objects.create(user=self.owner, company=self.company)
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        SubscriptionService.activate_plan(
            SubscriptionService.get_or_create_trial(self.company),
            seed_test_plans()["starter"],
            actor=self.owner,
        )

    def test_owner_can_cancel(self):
        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        url = reverse("subscription-cancel", kwargs={"version": "v1"})
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "cancelled")


class InvoiceCreationSubscriptionGateTests(TestCase):
    """The one real entitlement-enforcement point wired up this phase —
    see apps/invoices/views.py::InvoiceViewSet.get_permissions."""

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="789789789")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("invoice-list", kwargs={"version": "v1"})
        from apps.clients.models import Client

        self.client_obj = Client.objects.create(company=self.company, name="Klijent")

    def _payload(self):
        return {
            "client": self.client_obj.id,
            "issue_date": "2026-01-01",
            "due_date": "2026-01-15",
            "service_date": "2026-01-01",
            "items": [{"description": "Usluga", "quantity": "1", "unit_price": "1000.00"}],
        }

    def test_allowed_when_no_subscription_row_exists(self):
        response = self.client.post(
            self.url, self._payload(), content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_allowed_while_trialing(self):
        SubscriptionService.get_or_create_trial(self.company)
        response = self.client.post(
            self.url, self._payload(), content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_blocked_when_expired(self):
        subscription = SubscriptionService.get_or_create_trial(self.company)
        subscription.status = Subscription.Status.EXPIRED
        subscription.save(update_fields=["status"])
        response = self.client.post(
            self.url, self._payload(), content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 403)

    def test_blocked_when_cancelled(self):
        subscription = SubscriptionService.get_or_create_trial(self.company)
        subscription.status = Subscription.Status.CANCELLED
        subscription.save(update_fields=["status"])
        response = self.client.post(
            self.url, self._payload(), content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 403)

    def test_list_remains_open_when_expired(self):
        subscription = SubscriptionService.get_or_create_trial(self.company)
        subscription.status = Subscription.Status.EXPIRED
        subscription.save(update_fields=["status"])
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
