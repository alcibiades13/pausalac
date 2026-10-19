from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.services import InvoiceService
from apps.limits.testing import seed_test_rules


def _issued_invoice(company, client_obj, *, unit_price):
    today = timezone.now().date()
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=today,
        service_date=today,
        notes="",
        line_items=[{"description": "Usluga", "quantity": "1", "unit_price": unit_price}],
    )
    return InvoiceService.issue(invoice, actor=None)


class LimitsViewTests(TestCase):
    def setUp(self):
        seed_test_rules()
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("limits", kwargs={"version": "v1"})
        self.simulate_url = reverse("limits-simulate", kwargs={"version": "v1"})
        self.history_url = reverse("limits-pausal-history", kwargs={"version": "v1"})

    def test_get_limits_returns_both_trackers(self):
        _issued_invoice(self.company, self.client_obj, unit_price="1000000.00")
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("pausal_limit", body)
        self.assertIn("vat_threshold", body)
        self.assertEqual(Decimal(body["pausal_limit"]["current"]), Decimal("1000000.00"))
        self.assertEqual(body["pausal_limit"]["period"]["type"], "calendar_year")
        self.assertEqual(body["vat_threshold"]["period"]["type"], "trailing_12_months")

    def test_simulate_returns_before_and_after(self):
        _issued_invoice(self.company, self.client_obj, unit_price="1000000.00")
        response = self.client.post(
            self.simulate_url,
            {"amount": "800000.00"},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(Decimal(body["before"]["pausal_limit"]["current"]), Decimal("1000000.00"))
        self.assertEqual(Decimal(body["after"]["pausal_limit"]["current"]), Decimal("1800000.00"))

    def test_simulate_rejects_non_positive_amount(self):
        response = self.client.post(
            self.simulate_url, {"amount": "0"}, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 400)

    def test_simulate_rejects_invalid_amount(self):
        response = self.client.post(
            self.simulate_url,
            {"amount": "not-a-number"},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        _issued_invoice(other_company, other_client, unit_price="5000000.00")

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(Decimal(body["pausal_limit"]["current"]), Decimal("0.00"))

    def test_history_returns_monthly_breakdown_for_requested_year(self):
        _issued_invoice(self.company, self.client_obj, unit_price="500000.00")
        # A past year always has all 12 months of history (nothing left
        # to project) — the current year's history only runs through
        # "today"'s month, tested separately below.
        response = self.client.get(f"{self.history_url}?year=2020", **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["year"], 2020)
        self.assertEqual(len(body["history"]), 12)
        self.assertEqual(body["projection"], [])
        self.assertEqual(Decimal(body["threshold"]), Decimal("6000000.00"))

    def test_history_for_current_year_runs_through_this_month_only(self):
        response = self.client.get(f"{self.history_url}?year={timezone.now().date().year}", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["history"]), timezone.now().date().month)

    def test_history_defaults_to_current_year_without_query_param(self):
        response = self.client.get(self.history_url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["year"], timezone.now().date().year)

    def test_history_rejects_invalid_year(self):
        response = self.client.get(f"{self.history_url}?year=not-a-year", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_accountant_can_view_limits(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
