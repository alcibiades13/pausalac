from datetime import timedelta
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.services import InvoiceService
from apps.limits.testing import seed_test_rules
from apps.payments.models import Payment
from apps.payments.services import PaymentService


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


class InvoiceDocumentTypeApiTests(TestCase):
    """Phase 6c — the API-boundary half of the document_type behavior:
    creation, filtering, immutability, and the convert action. Ledger-
    level behavior (KPO/FinancialEvent/limits) is covered directly against
    InvoiceService in test_document_types.py."""

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.list_url = reverse("invoice-list", kwargs={"version": "v1"})

    def _create(self, document_type=None):
        payload = {
            "client": self.client_obj.id,
            **_dates(),
            "items": [{"description": "X", "quantity": "1", "unit_price": "1000"}],
        }
        if document_type is not None:
            payload["document_type"] = document_type
        return self.client.post(
            self.list_url, payload, content_type="application/json", **self.headers
        )

    def test_create_without_document_type_defaults_to_invoice(self):
        response = self._create()
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()["document_type"], "invoice")

    def test_create_profaktura_and_avans(self):
        profaktura = self._create("profaktura")
        avans = self._create("avans")
        self.assertEqual(profaktura.json()["document_type"], "profaktura")
        self.assertEqual(avans.json()["document_type"], "avans")

    def test_filter_by_document_type(self):
        self._create("invoice")
        self._create("profaktura")
        self._create("profaktura")

        response = self.client.get(self.list_url, {"document_type": "profaktura"}, **self.headers)
        results = response.json()["results"]
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["document_type"] == "profaktura" for r in results))

    def test_document_type_cannot_be_changed_after_creation(self):
        invoice_id = self._create("profaktura").json()["id"]
        detail_url = reverse("invoice-detail", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.patch(
            detail_url,
            {"document_type": "invoice"},
            content_type="application/json",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_convert_issued_profaktura_to_invoice(self):
        profaktura_id = self._create("profaktura").json()["id"]
        issue_url = reverse("invoice-issue", kwargs={"version": "v1", "pk": profaktura_id})
        self.client.post(issue_url, **self.headers)

        convert_url = reverse("invoice-convert", kwargs={"version": "v1", "pk": profaktura_id})
        response = self.client.post(convert_url, **self.headers)
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertEqual(body["document_type"], "invoice")
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["converted_from"], profaktura_id)

        profaktura_detail = self.client.get(
            reverse("invoice-detail", kwargs={"version": "v1", "pk": profaktura_id}),
            **self.headers,
        ).json()
        self.assertEqual(profaktura_detail["converted_to"], body["id"])

    def test_convert_draft_profaktura_is_rejected(self):
        profaktura_id = self._create("profaktura").json()["id"]
        convert_url = reverse("invoice-convert", kwargs={"version": "v1", "pk": profaktura_id})
        response = self.client.post(convert_url, **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_cannot_record_payment_against_profaktura(self):
        profaktura_id = self._create("profaktura").json()["id"]
        issue_url = reverse("invoice-issue", kwargs={"version": "v1", "pk": profaktura_id})
        self.client.post(issue_url, **self.headers)

        response = self.client.post(
            reverse("payment-list", kwargs={"version": "v1"}),
            {
                "invoice": profaktura_id,
                "amount": "1000.00",
                "paid_at": timezone.now().date().isoformat(),
                "method": "bank_transfer",
                "notes": "",
            },
            content_type="application/json",
            **self.headers,
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


class InvoicePdfTests(TestCase):
    """
    apps/invoices/views.py::InvoiceViewSet.pdf deliberately bypasses the
    X-Company-Id header mechanism (a plain <a href> download can't set a
    custom header) — resolves tenancy from the invoice's own company
    instead, mirroring CompanyViewSet's own-id addressing.
    """

    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        self.client_a = Client.objects.create(company=self.company_a, name="Klijent A")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)

        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        create_response = self.client.post(
            reverse("invoice-list", kwargs={"version": "v1"}),
            {
                "client": self.client_a.id,
                **_dates(),
                "items": [{"description": "X", "quantity": "1", "unit_price": "1"}],
            },
            content_type="application/json",
            HTTP_X_COMPANY_ID=str(self.company_a.id),
        )
        self.invoice_id = create_response.json()["id"]
        self.client.logout()

    def test_owner_can_download_pdf_without_company_header(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("invoice-pdf", kwargs={"version": "v1", "pk": self.invoice_id})
        response = self.client.get(url)  # no X-Company-Id header on purpose
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_other_companys_member_cannot_download_pdf(self):
        self.client.login(username="b@pausalac.rs", password="s3cr3t-pass")
        url = reverse("invoice-pdf", kwargs={"version": "v1", "pk": self.invoice_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_pdf_requires_authentication(self):
        url = reverse("invoice-pdf", kwargs={"version": "v1", "pk": self.invoice_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class InvoiceSendTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_with_email = Client.objects.create(
            company=self.company, name="Klijent A", email="klijent@primer.rs"
        )
        self.client_without_email = Client.objects.create(company=self.company, name="Klijent B")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}

    def _create_and_issue(self, client_obj):
        create_response = self.client.post(
            reverse("invoice-list", kwargs={"version": "v1"}),
            {
                "client": client_obj.id,
                **_dates(),
                "items": [{"description": "X", "quantity": "1", "unit_price": "1000"}],
            },
            content_type="application/json",
            **self.headers,
        )
        invoice_id = create_response.json()["id"]
        self.client.post(
            reverse("invoice-issue", kwargs={"version": "v1", "pk": invoice_id}), **self.headers
        )
        return invoice_id

    def test_cannot_send_a_draft(self):
        create_response = self.client.post(
            reverse("invoice-list", kwargs={"version": "v1"}),
            {
                "client": self.client_with_email.id,
                **_dates(),
                "items": [{"description": "X", "quantity": "1", "unit_price": "1"}],
            },
            content_type="application/json",
            **self.headers,
        )
        invoice_id = create_response.json()["id"]
        url = reverse("invoice-send", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_sending_without_a_client_email_requires_an_override(self):
        invoice_id = self._create_and_issue(self.client_without_email)
        url = reverse("invoice-send", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.post(url, **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_send_queues_email_and_eventually_marks_sent(self):
        invoice_id = self._create_and_issue(self.client_with_email)
        url = reverse("invoice-send", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.post(
            url, {"message": "Hvala na saradnji!"}, content_type="application/json", **self.headers
        )
        self.assertEqual(response.status_code, 202)

        # CELERY_TASK_ALWAYS_EAGER (config/settings/test.py) runs the task
        # synchronously, so by the time the response above returns, the
        # send -> mark_sent chain has already completed.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["klijent@primer.rs"])
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        self.assertIn("Hvala na saradnji!", mail.outbox[0].body)

        detail_url = reverse("invoice-detail", kwargs={"version": "v1", "pk": invoice_id})
        detail = self.client.get(detail_url, **self.headers).json()
        self.assertEqual(detail["status"], "sent")


class InvoiceDuplicateApiTests(TestCase):
    """Master prompt §94 — see apps.invoices.tests.test_duplication for
    the service-layer behavior; this is just the API-boundary proof."""

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}

    def test_duplicate_action_returns_a_new_draft(self):
        create_response = self.client.post(
            reverse("invoice-list", kwargs={"version": "v1"}),
            {
                "client": self.client_obj.id,
                **_dates(),
                "items": [{"description": "X", "quantity": "1", "unit_price": "1000"}],
            },
            content_type="application/json",
            **self.headers,
        )
        invoice_id = create_response.json()["id"]
        issue_url = reverse("invoice-issue", kwargs={"version": "v1", "pk": invoice_id})
        self.client.post(issue_url, **self.headers)

        duplicate_url = reverse("invoice-duplicate", kwargs={"version": "v1", "pk": invoice_id})
        response = self.client.post(duplicate_url, **self.headers)
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertNotEqual(body["id"], invoice_id)
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["total"], "1000.00")


class InvoiceStatusBreakdownApiTests(TestCase):
    """For `InvoiceStatusBreakdown` — same computation DashboardView's
    `outstanding` field exposes, reached here without a full dashboard
    fetch (apps.invoices.ledger.outstanding_summary)."""

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("invoice-status-breakdown", kwargs={"version": "v1"})

    def _issued_invoice(self, *, unit_price="1000.00", due_date=None):
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=due_date or today,
            service_date=today,
            notes="",
            line_items=[{"description": "Usluga", "quantity": "1", "unit_price": unit_price}],
        )
        return InvoiceService.issue(invoice, actor=None)

    def test_matches_dashboard_outstanding_figures(self):
        seed_test_rules()
        past_due = timezone.now().date() - timedelta(days=5)
        self._issued_invoice(unit_price="500.00", due_date=past_due)
        InvoiceService.mark_overdue_all()
        paid = self._issued_invoice(unit_price="1000.00")
        PaymentService.record_payment(
            invoice=paid,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.owner,
        )

        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["overdue_count"], 1)
        self.assertEqual(Decimal(str(body["overdue_total"])), Decimal("500.00"))
        self.assertEqual(Decimal(str(body["paid_ytd"])), Decimal("1000.00"))

        dashboard_body = self.client.get(
            reverse("dashboard", kwargs={"version": "v1"}), **self.headers
        ).json()
        self.assertEqual(body, dashboard_body["outstanding"])

    def test_empty_company_returns_zeroed_summary(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["count"], 0)
        self.assertEqual(Decimal(str(body["total"])), Decimal("0.00"))
        self.assertEqual(Decimal(str(body["paid_ytd"])), Decimal("0.00"))

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        other_owner = User.objects.create_user(email="other@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=other_owner, company=other_company)
        InvoiceService.issue(
            InvoiceService.create_draft(
                company=other_company,
                client=other_client,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date(),
                service_date=timezone.now().date(),
                notes="",
                line_items=[
                    {"description": "Usluga", "quantity": "1", "unit_price": "1000.00"}
                ],
            ),
            actor=None,
        )

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["count"], 0)
