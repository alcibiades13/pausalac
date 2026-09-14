from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.services import InvoiceService


def _issue_invoice_via_api(client, company, client_obj, headers):
    today = timezone.now().date().isoformat()
    response = client.post(
        reverse("invoice-list", kwargs={"version": "v1"}),
        {
            "client": client_obj.id,
            "issue_date": today,
            "due_date": today,
            "service_date": today,
            "items": [{"description": "Usluga", "quantity": "1", "unit_price": "1000"}],
        },
        content_type="application/json",
        **headers,
    )
    invoice_id = response.json()["id"]
    client.post(reverse("invoice-issue", kwargs={"version": "v1", "pk": invoice_id}), **headers)
    return invoice_id


class PaymentCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.invoice_id = _issue_invoice_via_api(
            self.client, self.company, self.client_obj, self.headers
        )
        self.list_url = reverse("payment-list", kwargs={"version": "v1"})

    def test_record_a_payment(self):
        response = self.client.post(
            self.list_url,
            {
                "invoice": self.invoice_id,
                "amount": "1000.00",
                "paid_at": timezone.now().date().isoformat(),
                "method": "bank_transfer",
            },
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 201, response.content)

        invoice_url = reverse("invoice-detail", kwargs={"version": "v1", "pk": self.invoice_id})
        invoice = self.client.get(invoice_url, **self.headers).json()
        self.assertEqual(invoice["status"], "paid")

    def test_cannot_use_another_companys_invoice(self):
        # Built directly via the service, not the API — self.owner has no
        # membership on other_company, so an API round-trip would just
        # 403 on invoice creation itself rather than exercising the check
        # this test is actually after (payment.validate_invoice).
        other_company = Company.objects.create(name="Firma B")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        today = timezone.now().date()
        other_invoice = InvoiceService.issue(
            InvoiceService.create_draft(
                company=other_company,
                client=other_client,
                issue_date=today,
                due_date=today,
                service_date=today,
                notes="",
                line_items=[{"description": "X", "quantity": "1", "unit_price": "1000"}],
            ),
            actor=None,
        )
        response = self.client.post(
            self.list_url,
            {
                "invoice": other_invoice.id,
                "amount": "1000.00",
                "paid_at": timezone.now().date().isoformat(),
            },
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_list_filters_by_invoice(self):
        self.client.post(
            self.list_url,
            {
                "invoice": self.invoice_id,
                "amount": "500.00",
                "paid_at": timezone.now().date().isoformat(),
            },
            content_type="application/json",
            **self.headers,
        )
        response = self.client.get(self.list_url, {"invoice": self.invoice_id}, **self.headers)
        self.assertEqual(response.json()["count"], 1)


class PaymentTenantIsolationTests(TestCase):
    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)

    def test_cannot_use_mismatched_company_header(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("payment-list", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_b.id))
        self.assertEqual(response.status_code, 403)


class PaymentRbacTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.accountant = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(user=self.owner, company=self.company)
        Membership.objects.create(
            user=self.accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}

        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.invoice_id = _issue_invoice_via_api(
            self.client, self.company, self.client_obj, self.headers
        )
        self.client.logout()

    def test_accountant_can_list_but_not_record_payments(self):
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        list_url = reverse("payment-list", kwargs={"version": "v1"})
        self.assertEqual(self.client.get(list_url, **self.headers).status_code, 200)

        response = self.client.post(
            list_url,
            {
                "invoice": self.invoice_id,
                "amount": "1000.00",
                "paid_at": timezone.now().date().isoformat(),
            },
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 403)
