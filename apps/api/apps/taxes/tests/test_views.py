from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.taxes.services import TaxService
from apps.taxes.testing import seed_test_rates

RESOLUTION_PAYLOAD = {
    "effective_from": "2026-01-01",
    "effective_until": "2026-03-31",
    "tax_base": "100000.00",
    "income_tax_amount": "10000.00",
    "pio_amount": "24000.00",
    "health_amount": "10300.00",
    "unemployment_amount": "750.00",
    "notes": "",
}


class TaxResolutionViewSetTests(TestCase):
    def setUp(self):
        seed_test_rates()
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.list_url = reverse("tax-resolution-list", kwargs={"version": "v1"})

    def test_create_generates_correct_obligation_count(self):
        response = self.client.post(
            self.list_url, RESOLUTION_PAYLOAD, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["rate_check_warnings"], [])

        obligations_url = reverse("tax-obligation-list", kwargs={"version": "v1"})
        obligations = self.client.get(obligations_url, **self.headers).json()
        self.assertEqual(obligations["count"], 3)

    def test_create_surfaces_rate_mismatch_warning(self):
        payload = {**RESOLUTION_PAYLOAD, "income_tax_amount": "99999.00"}
        response = self.client.post(
            self.list_url, payload, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(len(response.json()["rate_check_warnings"]) > 0)

    def test_accountant_cannot_create(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.list_url, RESOLUTION_PAYLOAD, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 403)

    def test_accountant_can_list(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")
        response = self.client.get(self.list_url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        self.client.post(
            self.list_url, RESOLUTION_PAYLOAD, content_type="application/json", **self.headers
        )
        # A member-less header would 403; add a membership on the other
        # company instead, to confirm zero *results*, not an access error.
        Membership.objects.create(user=self.owner, company=other_company)
        response = self.client.get(self.list_url, HTTP_X_COMPANY_ID=str(other_company.id))
        self.assertEqual(response.json()["count"], 0)


class TaxObligationViewSetTests(TestCase):
    def setUp(self):
        seed_test_rates()
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        self.obligation = self.resolution.obligations.get()

    def test_status_filter(self):
        url = reverse("tax-obligation-list", kwargs={"version": "v1"})
        response = self.client.get(url, {"status": "overdue"}, **self.headers)
        self.assertEqual(response.json()["count"], 0)
        response = self.client.get(url, {"status": "pending"}, **self.headers)
        self.assertEqual(response.json()["count"], 1)

    def test_mark_paid(self):
        url = reverse(
            "tax-obligation-mark-paid", kwargs={"version": "v1", "pk": self.obligation.id}
        )
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "paid")

    def test_accountant_cannot_mark_paid(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")
        url = reverse(
            "tax-obligation-mark-paid", kwargs={"version": "v1", "pk": self.obligation.id}
        )
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 403)


class CheckOverdueTaxObligationsCommandTests(TestCase):
    def test_command_flips_overdue(self):
        from io import StringIO

        from django.core.management import call_command

        company = Company.objects.create(name="Firma A", pib="123456789")
        seed_test_rates()
        past_month = date(timezone.now().year - 1, 1, 1)
        resolution = TaxService.create_resolution(
            company,
            effective_from=past_month,
            effective_until=past_month,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        out = StringIO()
        call_command("check_overdue_tax_obligations", stdout=out)
        obligation = resolution.obligations.get()
        self.assertEqual(obligation.status, "overdue")
        self.assertIn("1", out.getvalue())
