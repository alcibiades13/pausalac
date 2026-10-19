from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
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


def _issued_invoice(company, client_obj, *, unit_price="1000.00", due_date=None):
    today = timezone.now().date()
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=due_date or today,
        service_date=today,
        notes="",
        line_items=[{"description": "Usluga", "quantity": "1", "unit_price": unit_price}],
    )
    return InvoiceService.issue(invoice, actor=None)


class DashboardTests(TestCase):
    def setUp(self):
        seed_test_rules()
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.owner.email_verified_at = timezone.now()
        self.owner.save(update_fields=["email_verified_at"])
        self.company = Company.objects.create(
            name="Firma A", pib="123456789", bank_account="RS35..."
        )
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("dashboard", kwargs={"version": "v1"})

    def test_healthy_company_with_no_activity(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "ok")
        self.assertEqual(body["attention"], [])
        self.assertEqual(Decimal(str(body["revenue"]["ytd"])), Decimal("0.00"))
        self.assertEqual(body["revenue"]["basis"], "invoiced")
        self.assertEqual(body["outstanding"]["count"], 0)
        self.assertIn("limits", body)
        self.assertIn("pausal_limit", body["limits"])
        self.assertIn("vat_threshold", body["limits"])
        self.assertIsNone(body["next_obligation"])

    def test_revenue_monthly_series_covers_the_whole_calendar_year(self):
        # All 12 months, including ones still in the future — the chart
        # shows the year's shape end to end, future months zero-filled
        # rather than the series just stopping at "today".
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        series = body["revenue"]["monthly_series"]
        self.assertEqual(len(series), 12)
        self.assertEqual(series[0]["month"], f"{timezone.now().date().year}-01-01")
        self.assertTrue(all(Decimal(str(row["amount"])) == Decimal("0.00") for row in series))

    def test_outstanding_paid_ytd_reflects_paid_invoices_only(self):
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="50000.00")
        PaymentService.record_payment(
            invoice,
            amount=Decimal("50000.00"),
            paid_at=timezone.now().date(),
            method="bank_transfer",
            notes="",
            actor=None,
        )
        # Outstanding invoice, not paid — must not leak into paid_ytd.
        _issued_invoice(self.company, self.client_obj, unit_price="10000.00")

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(Decimal(str(body["outstanding"]["paid_ytd"])), Decimal("50000.00"))

    def test_tax_resolution_without_document_produces_attention_entry(self):
        from datetime import date
        from decimal import Decimal as D

        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "attention")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("tax_resolution_missing_document", types)

    def test_linking_a_document_clears_the_attention_entry(self):
        from datetime import date
        from decimal import Decimal as D

        from apps.documents.services import DocumentService
        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        DocumentService.upload(
            self.company,
            uploaded_by=self.owner,
            category="tax_resolution",
            title="Rešenje",
            description="",
            file_obj=SimpleUploadedFile("r.pdf", b"%PDF-1.4", content_type="application/pdf"),
            tax_resolution=resolution,
        )

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        types = [item["type"] for item in body["attention"]]
        self.assertNotIn("tax_resolution_missing_document", types)

    def test_pending_obligation_appears_as_next_obligation_without_affecting_health(self):
        from datetime import timedelta
        from decimal import Decimal as D

        from apps.documents.services import DocumentService
        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        future_month = (timezone.now().date().replace(day=1) + timedelta(days=60)).replace(day=1)
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=future_month,
            effective_until=future_month,
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        # Document attached so this test isolates "does a pending
        # obligation affect health" from the separate missing-document
        # attention source (apps.documents, Phase 3e).
        DocumentService.upload(
            self.company,
            uploaded_by=self.owner,
            category="tax_resolution",
            title="Rešenje",
            description="",
            file_obj=SimpleUploadedFile("r.pdf", b"%PDF-1.4", content_type="application/pdf"),
            tax_resolution=resolution,
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertIsNotNone(body["next_obligation"])
        self.assertEqual(body["next_obligation"]["status"], "pending")
        self.assertEqual(Decimal(body["next_obligation"]["total_amount"]), Decimal("45050.00"))
        self.assertEqual(body["business_health"]["status"], "ok")

    def test_overdue_obligation_flips_health_to_critical(self):
        from datetime import date
        from decimal import Decimal as D

        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        past_month = date(timezone.now().year - 1, 1, 1)
        TaxService.create_resolution(
            self.company,
            effective_from=past_month,
            effective_until=past_month,
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        TaxService.mark_overdue_all()

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        # An overdue obligation is never "next" — it already surfaces via
        # the tax_obligation_overdue attention item below; with no pending
        # obligation in this scenario, "next" is genuinely empty.
        self.assertIsNone(body["next_obligation"])
        self.assertEqual(body["business_health"]["status"], "critical")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("tax_obligation_overdue", types)

    def test_overdue_obligation_does_not_hide_a_genuinely_upcoming_one(self):
        from datetime import date, timedelta
        from decimal import Decimal as D

        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        past_month = date(timezone.now().year - 1, 1, 1)
        TaxService.create_resolution(
            self.company,
            effective_from=past_month,
            effective_until=past_month,
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        TaxService.mark_overdue_all()

        future_month = (timezone.now().date().replace(day=1) + timedelta(days=60)).replace(day=1)
        TaxService.create_resolution(
            self.company,
            effective_from=future_month,
            effective_until=future_month,
            tax_base=D("50000.00"),
            income_tax_amount=D("5000.00"),
            pio_amount=D("12000.00"),
            health_amount=D("5150.00"),
            unemployment_amount=D("375.00"),
        )

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["next_obligation"]["status"], "pending")
        self.assertEqual(Decimal(body["next_obligation"]["total_amount"]), Decimal("22525.00"))
        types = [item["type"] for item in body["attention"]]
        self.assertIn("tax_obligation_overdue", types)

    def test_next_obligation_is_deterministic_when_two_share_a_due_date(self):
        # Nothing in the model stops two obligations from sharing a
        # due_date. `.order_by("due_date")` alone leaves the choice
        # between tied rows to the database's own unspecified order —
        # deterministic within one run, but not guaranteed stable
        # between runs. `id` as a secondary sort key removes that.
        from datetime import date
        from decimal import Decimal as D

        from apps.taxes.models import TaxObligation
        from apps.taxes.services import TaxService
        from apps.taxes.testing import seed_test_rates

        seed_test_rates()
        shared_due_date = date(timezone.now().year, 12, 15)
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(timezone.now().year, 11, 1),
            effective_until=date(timezone.now().year, 11, 1),
            tax_base=D("100000.00"),
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        obligation = resolution.obligations.get()
        obligation.due_date = shared_due_date
        obligation.save(update_fields=["due_date"])

        later_duplicate = TaxObligation.objects.create(
            company=self.company,
            resolution=resolution,
            # A different period_start (the unique constraint is on
            # company+period_start, not company+due_date) — the point
            # here is only that two rows can share a due_date.
            period_start=date(timezone.now().year, 10, 1),
            due_date=shared_due_date,
            income_tax_amount=D("10000.00"),
            pio_amount=D("24000.00"),
            health_amount=D("10300.00"),
            unemployment_amount=D("750.00"),
        )
        self.assertGreater(later_duplicate.id, obligation.id)

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["next_obligation"]["due_date"], shared_due_date.isoformat())
        # The lower-id row wins consistently, not whichever the database
        # happens to return first for the tied due_date.
        self.assertEqual(Decimal(body["next_obligation"]["total_amount"]), obligation.total_amount)

    def test_limit_at_warning_level_produces_attention_without_being_critical(self):
        # 5,100,000 / 6,000,000 = 85% -> "warning", not "critical".
        _issued_invoice(self.company, self.client_obj, unit_price="5100000.00")
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "attention")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("limit_warning", types)

    def test_limit_at_critical_level_flips_health_to_critical(self):
        # 5,700,000 / 6,000,000 = 95% -> "critical".
        _issued_invoice(self.company, self.client_obj, unit_price="5700000.00")
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "critical")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("limit_warning", types)

    def test_issued_invoice_counts_as_revenue_and_outstanding(self):
        _issued_invoice(self.company, self.client_obj, unit_price="1000.00")
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(Decimal(body["revenue"]["ytd"]), Decimal("1000.00"))
        self.assertEqual(body["outstanding"]["count"], 1)
        self.assertEqual(Decimal(body["outstanding"]["total"]), Decimal("1000.00"))
        self.assertEqual(body["business_health"]["status"], "ok")

    def test_cancelling_an_issued_invoice_nets_out_of_revenue(self):
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="1000.00")
        InvoiceService.cancel(invoice, actor=None)
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(Decimal(body["revenue"]["ytd"]), Decimal("0.00"))
        self.assertEqual(body["outstanding"]["count"], 0)

    def test_partial_payment_reduces_outstanding_without_changing_revenue(self):
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="1000.00")
        PaymentService.record_payment(
            invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.owner,
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(Decimal(body["revenue"]["ytd"]), Decimal("1000.00"))
        self.assertEqual(Decimal(body["outstanding"]["total"]), Decimal("600.00"))

    def test_fully_paid_invoice_drops_out_of_outstanding(self):
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="1000.00")
        PaymentService.record_payment(
            invoice,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.owner,
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["outstanding"]["count"], 0)
        self.assertEqual(Decimal(body["revenue"]["ytd"]), Decimal("1000.00"))

    def test_overdue_invoice_makes_health_critical_with_attention_entry(self):
        past_due = timezone.now().date() - timedelta(days=5)
        _issued_invoice(self.company, self.client_obj, unit_price="500.00", due_date=past_due)
        InvoiceService.mark_overdue_all()

        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "critical")
        self.assertEqual(body["outstanding"]["overdue_count"], 1)
        self.assertEqual(Decimal(body["outstanding"]["overdue_total"]), Decimal("500.00"))
        types = [item["type"] for item in body["attention"]]
        self.assertIn("overdue_invoices", types)

    def test_unverified_email_makes_health_attention(self):
        self.owner.email_verified_at = None
        self.owner.save(update_fields=["email_verified_at"])
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "attention")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("email_unverified", types)

    def test_incomplete_onboarding_makes_health_attention(self):
        bare_company = Company.objects.create(name="Firma bez PIB-a")
        Membership.objects.create(user=self.owner, company=bare_company)
        response = self.client.get(self.url, HTTP_X_COMPANY_ID=str(bare_company.id))
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "attention")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("onboarding_incomplete", types)

    def test_expired_subscription_flips_health_to_critical(self):
        from apps.subscriptions.models import Subscription

        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.EXPIRED,
            trial_ends_at=timezone.now() - timedelta(days=1),
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "critical")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("subscription_inactive", types)

    def test_trial_ending_soon_produces_attention_not_critical(self):
        from apps.subscriptions.models import Subscription

        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() + timedelta(days=2),
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "attention")
        types = [item["type"] for item in body["attention"]]
        self.assertIn("trial_ending_soon", types)

    def test_active_subscription_produces_no_attention_entry(self):
        from apps.subscriptions.models import Subscription

        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.ACTIVE,
            trial_ends_at=timezone.now() - timedelta(days=20),
        )
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "ok")

    def test_sef_and_tax_document_gaps_alone_do_not_trigger_attention(self):
        # A fully-onboarded-as-far-as-possible company (company+bank+client
        # all done) still has sef/tax_document permanently "missing" per
        # compute_onboarding_status — that must NOT keep health at
        # "attention" forever once there's nothing actionable left.
        # setUp's company already has pib+bank_account+a client, and the
        # user's email is verified — only sef/tax_document remain missing.
        response = self.client.get(self.url, **self.headers)
        body = response.json()
        self.assertEqual(body["business_health"]["status"], "ok")


class DashboardTenantIsolationTests(TestCase):
    def setUp(self):
        seed_test_rules()
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        self.client_b = Client.objects.create(company=self.company_b, name="Klijent B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)
        _issued_invoice(self.company_b, self.client_b, unit_price="9999.00")

    def test_company_as_numbers_are_unaffected_by_company_bs_activity(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("dashboard", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_a.id))
        body = response.json()
        self.assertEqual(Decimal(body["revenue"]["ytd"]), Decimal("0.00"))

    def test_cannot_use_mismatched_company_header(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("dashboard", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_b.id))
        self.assertEqual(response.status_code, 403)


class DashboardRbacTests(TestCase):
    def test_accountant_can_view_dashboard(self):
        seed_test_rules()
        company = Company.objects.create(name="Firma A")
        accountant = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(user=accountant, company=company, role=Membership.Role.ACCOUNTANT)
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        url = reverse("dashboard", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(company.id))
        self.assertEqual(response.status_code, 200)
