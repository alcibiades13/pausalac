from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.models import FinancialEvent, Invoice
from apps.limits.testing import seed_test_rules
from apps.taxes.models import TaxObligation, TaxResolution

from ..dashboard import compute_client_portfolio, summarize_portfolio
from ..services import AccountingService

RESOLUTION_FIELDS = dict(
    tax_base=Decimal("100000.00"),
    income_tax_amount=Decimal("10000.00"),
    pio_amount=Decimal("24000.00"),
    health_amount=Decimal("10300.00"),
    unemployment_amount=Decimal("750.00"),
)


class ComputeClientPortfolioTests(TestCase):
    def setUp(self):
        seed_test_rules()
        self.admin = User.objects.create_user(email="admin@agencija.rs", password="s3cr3t-pass")
        self.org = AccountingService.create_organization(self.admin, name="Agencija A")
        self._pib_counter = 100000000

    def _next_pib(self) -> str:
        self._pib_counter += 1
        return str(self._pib_counter)

    def _connect_company(self, name: str) -> Company:
        company = Company.objects.create(name=name, pib=self._next_pib())
        owner = User.objects.create_user(
            email=f"owner{company.id}@firma.rs", password="s3cr3t-pass"
        )
        Membership.objects.create(user=owner, company=company)
        connection = AccountingService.create_connection(
            self.org, company_pib=company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.accept_connection(connection, actor=owner)
        return company

    def test_empty_when_no_active_connections(self):
        self.assertEqual(compute_client_portfolio(self.org), [])

    def test_clean_company_is_ok(self):
        company = self._connect_company("Firma Clean")
        portfolio = compute_client_portfolio(self.org)
        self.assertEqual(len(portfolio), 1)
        row = portfolio[0]
        self.assertEqual(row["company_id"], company.id)
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["overdue_invoice_count"], 0)
        self.assertEqual(row["missing_document_count"], 0)
        self.assertIsNone(row["next_obligation_due"])
        self.assertIsNone(row["integration_errors"])
        self.assertEqual(row["granted_role"], "accountant")

    def test_overdue_invoice_makes_company_critical(self):
        company = self._connect_company("Firma Overdue")
        client = Client.objects.create(company=company, name="Klijent")
        Invoice.objects.create(
            company=company,
            client=client,
            status=Invoice.Status.OVERDUE,
            issue_date=date.today(),
            due_date=date.today() - timedelta(days=5),
            service_date=date.today(),
            total=Decimal("10000.00"),
        )
        row = compute_client_portfolio(self.org)[0]
        self.assertEqual(row["status"], "critical")
        self.assertEqual(row["overdue_invoice_count"], 1)

    def test_critical_limit_makes_company_critical(self):
        company = self._connect_company("Firma Limit")
        FinancialEvent.objects.create(
            company=company,
            event_type=FinancialEvent.EventType.INVOICE_ISSUED,
            amount=Decimal("5800000.00"),
            currency="RSD",
        )
        row = compute_client_portfolio(self.org)[0]
        self.assertEqual(row["status"], "critical")
        self.assertEqual(row["pausal_limit"]["warning_level"], "critical")
        self.assertEqual(row["revenue_ytd"], Decimal("5800000.00"))

    def test_warning_tier_limit_makes_company_attention(self):
        company = self._connect_company("Firma Warning")
        FinancialEvent.objects.create(
            company=company,
            event_type=FinancialEvent.EventType.INVOICE_ISSUED,
            amount=Decimal("5200000.00"),
            currency="RSD",
        )
        row = compute_client_portfolio(self.org)[0]
        self.assertEqual(row["pausal_limit"]["warning_level"], "warning")
        self.assertEqual(row["status"], "attention")

    def test_missing_document_makes_company_attention(self):
        company = self._connect_company("Firma Doc")
        TaxResolution.objects.create(
            company=company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            **RESOLUTION_FIELDS,
        )
        row = compute_client_portfolio(self.org)[0]
        self.assertEqual(row["status"], "attention")
        self.assertEqual(row["missing_document_count"], 1)

    def test_overdue_obligation_makes_company_critical(self):
        company = self._connect_company("Firma Obligation")
        resolution = TaxResolution.objects.create(
            company=company,
            effective_from=date(2020, 1, 1),
            effective_until=date(2020, 1, 31),
            **RESOLUTION_FIELDS,
        )
        TaxObligation.objects.create(
            company=company,
            resolution=resolution,
            period_start=date(2020, 1, 1),
            due_date=date(2020, 2, 17),
            status=TaxObligation.Status.OVERDUE,
            income_tax_amount=RESOLUTION_FIELDS["income_tax_amount"],
            pio_amount=RESOLUTION_FIELDS["pio_amount"],
            health_amount=RESOLUTION_FIELDS["health_amount"],
            unemployment_amount=RESOLUTION_FIELDS["unemployment_amount"],
        )
        row = compute_client_portfolio(self.org)[0]
        self.assertEqual(row["status"], "critical")
        self.assertTrue(row["next_obligation_overdue"])
        self.assertEqual(row["next_obligation_due"], "2020-02-17")

    def test_summary_counts(self):
        self._connect_company("OK Co")
        critical_company = self._connect_company("Critical Co")
        client = Client.objects.create(company=critical_company, name="Klijent")
        Invoice.objects.create(
            company=critical_company,
            client=client,
            status=Invoice.Status.OVERDUE,
            issue_date=date.today(),
            due_date=date.today() - timedelta(days=5),
            service_date=date.today(),
            total=Decimal("10000.00"),
        )
        summary = summarize_portfolio(compute_client_portfolio(self.org))
        self.assertEqual(summary, {"total": 2, "ok": 1, "attention": 0, "critical": 1})

    def test_revoked_connection_excluded(self):
        company = self._connect_company("Firma Revoked")
        connection = self.org.connections.get(company=company)
        AccountingService.revoke_connection(connection, actor=self.admin)
        self.assertEqual(compute_client_portfolio(self.org), [])

    def test_query_count_is_independent_of_client_count(self):
        self._connect_company("A")
        with self.assertNumQueries(8):
            compute_client_portfolio(self.org)

        self._connect_company("B")
        self._connect_company("C")
        with self.assertNumQueries(8):
            compute_client_portfolio(self.org)
