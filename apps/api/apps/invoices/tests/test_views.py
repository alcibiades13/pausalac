from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership


def _dates():
    today = timezone.now().date().isoformat()
    return {"issue_date": today, "due_date": today, "service_date": today}


class InvoiceCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.list_url = reverse("invoice-list", kwargs={"version": "v1"})

    def _headers(self):
        return {"HTTP_X_COMPANY_ID": str(self.company.id)}

    def _create_draft(self):
        payload = {
            "client": self.client_obj.id,
            **_dates(),
            "items": [{"description": "Usluga", "quantity": "1", "unit_price": "1500.00"}],
        }
        response = self.client.post(
            self.list_url, payload, content_type="application/json", **self._headers()
        )
        return response

    def test_create_draft_invoice(self):
        response = self._create_draft()
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertEqual(body["status"], "draft")
        self.assertIsNone(body["invoice_number"])
        self.assertEqual(body["total"], "1500.00")

    def test_create_requires_at_least_one_line_item(self):
        payload = {"client": self.client_obj.id, **_dates(), "items": []}
        response = self.client.post(
            self.list_url, payload, content_type="application/json", **self._headers()
        )
        self.assertEqual(response.status_code, 400)

    def test_cannot_use_another_companys_client(self):
        other_company = Company.objects.create(name="Firma B")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        payload = {
            "client": other_client.id,
            **_dates(),
            "items": [{"description": "X", "quantity": "1", "unit_price": "1"}],
        }
        response = self.client.post(
            self.list_url, payload, content_type="application/json", **self._headers()
        )
        self.assertEqual(response.status_code, 400)

    def test_issue_then_cancel_lifecycle(self):
        invoice_id = self._create_draft().json()["id"]
        issue_url = reverse("invoice-issue", kwargs={"version": "v1", "pk": invoice_id})
        issue_response = self.client.post(issue_url, **self._headers())
        self.assertEqual(issue_response.status_code, 200)
        self.assertEqual(issue_response.json()["status"], "issued")
        self.assertIsNotNone(issue_response.json()["invoice_number"])

        cancel_url = reverse("invoice-cancel", kwargs={"version": "v1", "pk": invoice_id})
        cancel_response = self.client.post(cancel_url, **self._headers())
        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.json()["status"], "cancelled")

    def test_cannot_edit_after_issuing(self):
        invoice_id = self._create_draft().json()["id"]
        issue_url = reverse("invoice-issue", kwargs={"version": "v1", "pk": invoice_id})
        self.client.post(issue_url, **self._headers())

        detail_url = reverse("invoice-detail", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.patch(
            detail_url, {"notes": "izmena"}, content_type="application/json", **self._headers()
        )
        self.assertEqual(response.status_code, 400)


class InvoiceTenantIsolationTests(TestCase):
    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        self.client_b = Client.objects.create(company=self.company_b, name="Klijent B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)

        today = timezone.now().date().isoformat()
        self.client.login(username="b@pausalac.rs", password="s3cr3t-pass")
        payload = {
            "client": self.client_b.id,
            "issue_date": today,
            "due_date": today,
            "service_date": today,
            "items": [{"description": "X", "quantity": "1", "unit_price": "1"}],
        }
        response = self.client.post(
            reverse("invoice-list", kwargs={"version": "v1"}),
            payload,
            content_type="application/json",
            HTTP_X_COMPANY_ID=str(self.company_b.id),
        )
        self.invoice_b_id = response.json()["id"]
        self.client.logout()

    def test_other_companys_invoice_is_not_reachable(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("invoice-detail", kwargs={"version": "v1", "pk": self.invoice_b_id})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_a.id))
        self.assertEqual(response.status_code, 404)

    def test_cannot_use_mismatched_company_header(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("invoice-list", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_b.id))
        self.assertEqual(response.status_code, 403)


class InvoiceRbacTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        self.accountant = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        self.accountant_admin = User.objects.create_user(
            email="admin-accountant@pausalac.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(
            user=self.accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        Membership.objects.create(
            user=self.accountant_admin, company=self.company, role=Membership.Role.ACCOUNTANT_ADMIN
        )
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.payload = {
            "client": self.client_obj.id,
            **_dates(),
            "items": [{"description": "X", "quantity": "1", "unit_price": "1"}],
        }
        self.list_url = reverse("invoice-list", kwargs={"version": "v1"})

    def test_plain_accountant_cannot_create_invoice(self):
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        response = self.client.post(
            self.list_url, self.payload, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 403)

    def test_accountant_admin_can_create_but_not_cancel(self):
        self.client.login(username="admin-accountant@pausalac.rs", password="s3cr3t-pass")
        create_response = self.client.post(
            self.list_url, self.payload, content_type="application/json", **self.headers
        )
        self.assertEqual(create_response.status_code, 201)

        invoice_id = create_response.json()["id"]
        cancel_url = reverse("invoice-cancel", kwargs={"version": "v1", "pk": invoice_id})
        cancel_response = self.client.post(cancel_url, **self.headers)
        self.assertEqual(cancel_response.status_code, 403)
