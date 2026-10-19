from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.ledger import monthly_issued_revenue
from apps.invoices.models import FinancialEvent
from apps.invoices.services import InvoiceService


def _issued_invoice(company, client_obj, *, unit_price, on_date):
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=on_date,
        due_date=on_date,
        service_date=on_date,
        notes="",
        line_items=[{"description": "Usluga", "quantity": "1", "unit_price": unit_price}],
    )
    invoice = InvoiceService.issue(invoice, actor=None)
    # occurred_at is auto_now_add — backdate directly, same pattern
    # apps.limits.tests.test_services already uses for month-spanning data.
    FinancialEvent.objects.filter(invoice=invoice).update(
        occurred_at=timezone.make_aware(timezone.datetime(on_date.year, on_date.month, on_date.day))
    )
    return invoice


class MonthlyIssuedRevenueTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")

    def test_groups_by_month_with_zero_filled_gaps(self):
        _issued_invoice(
            self.company, self.client_obj, unit_price="100000.00", on_date=date(2026, 1, 15)
        )
        _issued_invoice(
            self.company, self.client_obj, unit_price="50000.00", on_date=date(2026, 3, 5)
        )
        rows = monthly_issued_revenue(self.company, date(2026, 1, 1), date(2026, 3, 31))
        self.assertEqual([r["month"] for r in rows], ["2026-01-01", "2026-02-01", "2026-03-01"])
        self.assertEqual(rows[0]["amount"], Decimal("100000.00"))
        self.assertEqual(rows[1]["amount"], Decimal("0.00"))
        self.assertEqual(rows[2]["amount"], Decimal("50000.00"))

    def test_cancellation_nets_out_within_the_same_month(self):
        invoice = _issued_invoice(
            self.company, self.client_obj, unit_price="200000.00", on_date=date(2026, 5, 10)
        )
        InvoiceService.cancel(invoice, actor=None)
        FinancialEvent.objects.filter(invoice=invoice, event_type=FinancialEvent.EventType.INVOICE_CANCELLED).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 5, 20))
        )
        rows = monthly_issued_revenue(self.company, date(2026, 5, 1), date(2026, 5, 31))
        self.assertEqual(rows[0]["amount"], Decimal("0.00"))

    def test_partial_range_only_sums_events_within_bounds(self):
        _issued_invoice(
            self.company, self.client_obj, unit_price="10000.00", on_date=date(2026, 9, 17)
        )
        rows = monthly_issued_revenue(self.company, date(2026, 9, 1), date(2026, 9, 16))
        self.assertEqual(rows[0]["amount"], Decimal("0.00"))

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        _issued_invoice(
            other_company, other_client, unit_price="500000.00", on_date=date(2026, 1, 1)
        )
        rows = monthly_issued_revenue(self.company, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(rows[0]["amount"], Decimal("0.00"))
