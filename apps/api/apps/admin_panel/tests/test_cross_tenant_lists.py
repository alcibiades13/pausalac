"""
Every list view here deliberately uses Model.objects.all() instead of
.for_company(...) — the one place in the codebase where bypassing tenant
scoping is correct, not a bug (views.py's own module docstring). One test
per list proves that's real, not an accident of copy-pasting a
tenant-scoped queryset.
"""

from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.services import AuditService
from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.services import DocumentService
from apps.invoices.models import Invoice
from apps.notifications.models import Notification
from apps.subscriptions.models import Plan, Subscription
from apps.taxes.models import TaxObligation, TaxResolution


class CrossTenantAdminListTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email="super@pausalac.rs", password="s3cr3t-pass", is_staff=True, is_superuser=True
        )
        self.client.login(username="super@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A", pib="111111111")
        self.company_b = Company.objects.create(name="Firma B", pib="222222222")
        self.today = timezone.now().date()

    def _get(self, name):
        return self.client.get(reverse(name, kwargs={"version": "v1"}))

    def test_company_list_spans_multiple_tenants(self):
        response = self._get("admin-company-list")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.json()["results"]}
        self.assertIn("Firma A", names)
        self.assertIn("Firma B", names)

    def test_subscription_list_spans_multiple_tenants(self):
        plan = Plan.objects.create(identifier="starter", name="Starter", price="1500.00")
        Subscription.objects.create(
            company=self.company_a,
            plan=plan,
            status=Subscription.Status.ACTIVE,
            trial_ends_at=timezone.now(),
        )
        Subscription.objects.create(
            company=self.company_b,
            plan=plan,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now(),
        )
        response = self._get("admin-subscription-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_invoice_list_spans_multiple_tenants(self):
        from apps.clients.models import Client

        client_a = Client.objects.create(company=self.company_a, name="Klijent A")
        client_b = Client.objects.create(company=self.company_b, name="Klijent B")
        Invoice.objects.create(
            company=self.company_a,
            client=client_a,
            issue_date=self.today,
            due_date=self.today,
            service_date=self.today,
            total=Decimal("1000.00"),
        )
        Invoice.objects.create(
            company=self.company_b,
            client=client_b,
            issue_date=self.today,
            due_date=self.today,
            service_date=self.today,
            total=Decimal("2000.00"),
        )
        response = self._get("admin-invoice-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_document_list_spans_multiple_tenants(self):
        DocumentService.upload(
            self.company_a,
            uploaded_by=None,
            category=Document.Category.OTHER,
            title="Doc A",
            description="",
            file_obj=SimpleUploadedFile("a.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )
        DocumentService.upload(
            self.company_b,
            uploaded_by=None,
            category=Document.Category.OTHER,
            title="Doc B",
            description="",
            file_obj=SimpleUploadedFile("b.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )
        response = self._get("admin-document-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_tax_obligation_list_spans_multiple_tenants(self):
        for company in (self.company_a, self.company_b):
            resolution = TaxResolution.objects.create(
                company=company,
                effective_from=self.today.replace(day=1),
                effective_until=self.today,
                tax_base=Decimal("1000.00"),
                income_tax_amount=Decimal("100.00"),
                pio_amount=Decimal("100.00"),
                health_amount=Decimal("100.00"),
                unemployment_amount=Decimal("100.00"),
            )
            TaxObligation.objects.create(
                company=company,
                resolution=resolution,
                period_start=self.today.replace(day=1),
                due_date=self.today,
                income_tax_amount=Decimal("100.00"),
                pio_amount=Decimal("100.00"),
                health_amount=Decimal("100.00"),
                unemployment_amount=Decimal("100.00"),
            )
        response = self._get("admin-tax-obligation-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_notification_list_spans_multiple_tenants(self):
        user_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        user_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        Notification.objects.create(
            company=self.company_a,
            recipient=user_a,
            event_type="test_event",
            dedup_key="a",
            priority=Notification.Priority.INFORMATIONAL,
            channel=Notification.Channel.IN_APP,
            title="A",
            message="A",
        )
        Notification.objects.create(
            company=self.company_b,
            recipient=user_b,
            event_type="test_event",
            dedup_key="b",
            priority=Notification.Priority.INFORMATIONAL,
            channel=Notification.Channel.IN_APP,
            title="B",
            message="B",
        )
        response = self._get("admin-notification-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_audit_log_list_spans_multiple_tenants(self):
        AuditService.log(
            company=self.company_a,
            entity_type="company",
            entity_id=self.company_a.id,
            action="created",
        )
        AuditService.log(
            company=self.company_b,
            entity_type="company",
            entity_id=self.company_b.id,
            action="created",
        )
        response = self._get("admin-audit-log-list")
        self.assertEqual(response.status_code, 200)
        company_ids = {row["company_id"] for row in response.json()["results"]}
        self.assertEqual(company_ids, {self.company_a.id, self.company_b.id})

    def test_company_members_view_returns_memberships_for_requested_company(self):
        from apps.companies.models import Membership

        owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=owner, company=self.company_a)
        response = self.client.get(
            reverse("admin-company-members", kwargs={"version": "v1", "pk": self.company_a.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_integrations_status_reflects_unset_sentry_dsn(self):
        response = self._get("admin-integrations-status")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["sentry"]["configured"])
        self.assertFalse(body["sef"]["configured"])
