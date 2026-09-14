from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import InvoiceLineItem
from apps.invoices.services import InvoiceService
from apps.kpo.models import KPOEntry


def _draft(company, client_obj, items, *, service_date=None):
    today = timezone.now().date()
    service_date = service_date or today
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=today,
        service_date=service_date,
        notes="",
        line_items=items,
    )


class KPOServiceIssueTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")

    def test_service_only_invoice_sums_into_service_column(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "1000.00",
                }
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        entry = KPOEntry.objects.get(invoice=invoice)
        self.assertEqual(entry.product_revenue, Decimal("0.00"))
        self.assertEqual(entry.service_revenue, Decimal("1000.00"))
        self.assertEqual(entry.total_revenue, Decimal("1000.00"))
        self.assertEqual(entry.entry_type, KPOEntry.EntryType.ORIGINAL)

    def test_product_only_invoice_sums_into_product_column(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Widget",
                    "item_type": "product",
                    "quantity": "2",
                    "unit_price": "500.00",
                }
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        entry = KPOEntry.objects.get(invoice=invoice)
        self.assertEqual(entry.product_revenue, Decimal("1000.00"))
        self.assertEqual(entry.service_revenue, Decimal("0.00"))

    def test_mixed_invoice_splits_correctly(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Widget",
                    "item_type": "product",
                    "quantity": "1",
                    "unit_price": "300.00",
                },
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "700.00",
                },
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        entry = KPOEntry.objects.get(invoice=invoice)
        self.assertEqual(entry.product_revenue, Decimal("300.00"))
        self.assertEqual(entry.service_revenue, Decimal("700.00"))
        self.assertEqual(entry.total_revenue, Decimal("1000.00"))

    def test_line_item_defaults_to_service_when_type_omitted(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [{"description": "Konsalting", "quantity": "1", "unit_price": "1000.00"}],
        )
        self.assertEqual(invoice.items.first().item_type, InvoiceLineItem.ItemType.SERVICE)

    def test_entry_date_is_service_date_not_issue_date(self):
        import datetime

        service_date = timezone.now().date() - datetime.timedelta(days=10)
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "1000.00",
                }
            ],
            service_date=service_date,
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        entry = KPOEntry.objects.get(invoice=invoice)
        self.assertNotEqual(invoice.issue_date, service_date)
        self.assertEqual(entry.entry_date, service_date)

    def test_sequence_number_increments_per_company(self):
        invoice1 = _draft(
            self.company,
            self.client_obj,
            [{"description": "A", "item_type": "service", "quantity": "1", "unit_price": "100.00"}],
        )
        invoice2 = _draft(
            self.company,
            self.client_obj,
            [{"description": "B", "item_type": "service", "quantity": "1", "unit_price": "200.00"}],
        )
        InvoiceService.issue(invoice1, actor=None)
        InvoiceService.issue(invoice2, actor=None)
        entries = list(KPOEntry.objects.for_company(self.company).order_by("sequence_number"))
        self.assertEqual([e.sequence_number for e in entries], [1, 2])

    def test_sequence_number_independent_across_companies(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")

        invoice_a = _draft(
            self.company,
            self.client_obj,
            [{"description": "A", "item_type": "service", "quantity": "1", "unit_price": "100.00"}],
        )
        invoice_b = _draft(
            other_company,
            other_client,
            [{"description": "B", "item_type": "service", "quantity": "1", "unit_price": "200.00"}],
        )
        InvoiceService.issue(invoice_a, actor=None)
        InvoiceService.issue(invoice_b, actor=None)

        entry_a = KPOEntry.objects.get(invoice=invoice_a)
        entry_b = KPOEntry.objects.get(invoice=invoice_b)
        self.assertEqual(entry_a.sequence_number, 1)
        self.assertEqual(entry_b.sequence_number, 1)

    def test_description_contains_invoice_number_and_client(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "1000.00",
                }
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        entry = KPOEntry.objects.get(invoice=invoice)
        self.assertIn(invoice.invoice_number, entry.description)
        self.assertIn("Klijent A", entry.description)


class KPOServiceCancelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")

    def test_cancelling_issued_invoice_creates_storno_row(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Widget",
                    "item_type": "product",
                    "quantity": "1",
                    "unit_price": "300.00",
                },
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "700.00",
                },
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        InvoiceService.cancel(invoice, actor=None)

        entries = list(KPOEntry.objects.filter(invoice=invoice).order_by("sequence_number"))
        self.assertEqual(len(entries), 2)
        original, storno = entries
        self.assertEqual(original.entry_type, KPOEntry.EntryType.ORIGINAL)
        self.assertEqual(storno.entry_type, KPOEntry.EntryType.STORNO)
        self.assertEqual(storno.product_revenue, -original.product_revenue)
        self.assertEqual(storno.service_revenue, -original.service_revenue)
        self.assertIn("Storno", storno.description)
        # Original untouched.
        self.assertEqual(original.product_revenue, Decimal("300.00"))
        self.assertEqual(original.service_revenue, Decimal("700.00"))

    def test_storno_gets_its_own_sequence_number(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "1000.00",
                }
            ],
        )
        invoice = InvoiceService.issue(invoice, actor=None)
        InvoiceService.cancel(invoice, actor=None)
        entries = list(KPOEntry.objects.filter(invoice=invoice).order_by("sequence_number"))
        self.assertEqual(entries[0].sequence_number, 1)
        self.assertEqual(entries[1].sequence_number, 2)

    def test_cancelling_a_draft_creates_no_kpo_entry(self):
        invoice = _draft(
            self.company,
            self.client_obj,
            [
                {
                    "description": "Konsalting",
                    "item_type": "service",
                    "quantity": "1",
                    "unit_price": "1000.00",
                }
            ],
        )
        InvoiceService.cancel(invoice, actor=None)
        self.assertEqual(KPOEntry.objects.filter(invoice=invoice).count(), 0)
