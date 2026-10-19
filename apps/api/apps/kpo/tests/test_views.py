from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.services import InvoiceService


def _issued_invoice(company, client_obj, *, service_date=None):
    today = timezone.now().date()
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=today,
        service_date=service_date or today,
        notes="",
        line_items=[
            {
                "description": "Konsalting",
                "item_type": "service",
                "quantity": "1",
                "unit_price": "1000.00",
            }
        ],
    )
    return InvoiceService.issue(invoice, actor=None)


class KPOEntryListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("kpo-list", kwargs={"version": "v1"})

    def test_lists_entries_for_the_company(self):
        _issued_invoice(self.company, self.client_obj)
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["results"][0]["sequence_number"], 1)

    def test_date_range_filter(self):
        import datetime

        old_date = timezone.now().date() - datetime.timedelta(days=100)
        _issued_invoice(self.company, self.client_obj, service_date=old_date)
        _issued_invoice(self.company, self.client_obj)

        response = self.client.get(
            self.url, {"date_from": timezone.now().date().isoformat()}, **self.headers
        )
        body = response.json()
        self.assertEqual(body["count"], 1)

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        _issued_invoice(other_company, other_client)

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["count"], 0)

    def test_accountant_can_view(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)


class KPOMonthlySummaryViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("kpo-monthly-summary", kwargs={"version": "v1"})

    def test_returns_twelve_months_for_a_past_year(self):
        response = self.client.get(f"{self.url}?year=2020", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 12)

    def test_defaults_to_current_year_without_query_param(self):
        import datetime
        from decimal import Decimal

        _issued_invoice(self.company, self.client_obj)
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        current_month = datetime.date.today().replace(day=1).isoformat()
        row = next(r for r in body if r["month"] == current_month)
        self.assertEqual(Decimal(str(row["services"])), Decimal("1000.00"))

    def test_rejects_invalid_year(self):
        response = self.client.get(f"{self.url}?year=not-a-year", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_tenant_isolation(self):
        from decimal import Decimal

        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        _issued_invoice(other_company, other_client)

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertTrue(all(Decimal(str(row["total"])) == Decimal("0.00") for row in body))


class KPOExportViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        _issued_invoice(self.company, self.client_obj)

    def test_pdf_export_succeeds_for_a_member(self):
        url = reverse("kpo-export-pdf", kwargs={"version": "v1", "company_id": self.company.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_xlsx_export_succeeds_for_a_member(self):
        url = reverse("kpo-export-xlsx", kwargs={"version": "v1", "company_id": self.company.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_404s_for_a_non_member(self):
        User.objects.create_user(email="stranger@pausalac.rs", password="s3cr3t-pass")
        self.client.logout()
        self.client.login(username="stranger@pausalac.rs", password="s3cr3t-pass")
        url = reverse("kpo-export-pdf", kwargs={"version": "v1", "company_id": self.company.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
