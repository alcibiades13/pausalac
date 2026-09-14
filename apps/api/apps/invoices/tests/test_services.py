from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import FinancialEvent, Invoice, InvoiceLineItem
from apps.invoices.services import InvalidTransitionError, InvoiceService


def _make_company_client_user():
    company = Company.objects.create(name="Firma A", default_currency="RSD")
    client = Client.objects.create(company=company, name="Klijent A")
    user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
    return company, client, user


class InvoiceServiceCreateTests(TestCase):
    def setUp(self):
        self.company, self.client_obj, self.user = _make_company_client_user()

    def test_create_draft_computes_total_from_line_items(self):
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=today,
            service_date=today,
            notes="",
            line_items=[
                {"description": "Konsalting", "quantity": "2", "unit_price": "1000.00"},
                {"description": "Dizajn", "quantity": "1", "unit_price": "500.50"},
            ],
        )
        self.assertEqual(invoice.total, Decimal("2500.50"))
        self.assertEqual(invoice.items.count(), 2)
        self.assertEqual(invoice.status, Invoice.Status.DRAFT)
        self.assertIsNone(invoice.invoice_number)

    def test_line_item_type_defaults_to_service_and_is_stored_when_given(self):
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=today,
            service_date=today,
            notes="",
            line_items=[
                {"description": "Konsalting", "quantity": "1", "unit_price": "1000.00"},
                {
                    "description": "Widget",
                    "item_type": "product",
                    "quantity": "1",
                    "unit_price": "500.00",
                },
            ],
        )
        items = list(invoice.items.order_by("position"))
        self.assertEqual(items[0].item_type, InvoiceLineItem.ItemType.SERVICE)
        self.assertEqual(items[1].item_type, InvoiceLineItem.ItemType.PRODUCT)

    def test_create_draft_defaults_currency_from_company(self):
        today = timezone.now().date()
        invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=today,
            service_date=today,
            notes="",
            line_items=[{"description": "X", "quantity": "1", "unit_price": "100"}],
        )
        self.assertEqual(invoice.currency, "RSD")


class InvoiceServiceIssueCancelTests(TestCase):
    def setUp(self):
        self.company, self.client_obj, self.user = _make_company_client_user()
        today = timezone.now().date()
        self.invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=today,
            service_date=today,
            notes="",
            line_items=[{"description": "Usluga", "quantity": "1", "unit_price": "1000.00"}],
        )

    def test_issue_assigns_number_and_creates_financial_event(self):
        invoice = InvoiceService.issue(self.invoice, actor=self.user)
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)
        self.assertTrue(invoice.invoice_number.startswith(f"INV-{invoice.issue_date.year}-"))
        self.assertIsNotNone(invoice.issued_at)

        events = FinancialEvent.objects.filter(invoice=invoice)
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, FinancialEvent.EventType.INVOICE_ISSUED)
        self.assertEqual(events.first().amount, Decimal("1000.00"))

    def test_cannot_issue_invoice_with_no_line_items(self):
        self.invoice.items.all().delete()
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.issue(self.invoice, actor=self.user)

    def test_cannot_issue_twice(self):
        InvoiceService.issue(self.invoice, actor=self.user)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.issue(self.invoice, actor=self.user)

    def test_cancel_draft_creates_no_financial_event(self):
        InvoiceService.cancel(self.invoice, actor=self.user)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.CANCELLED)
        self.assertEqual(FinancialEvent.objects.filter(invoice=self.invoice).count(), 0)

    def test_cancel_issued_invoice_creates_reversal_event(self):
        InvoiceService.issue(self.invoice, actor=self.user)
        InvoiceService.cancel(self.invoice, actor=self.user)
        events = list(FinancialEvent.objects.filter(invoice=self.invoice).order_by("id"))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, FinancialEvent.EventType.INVOICE_ISSUED)
        self.assertEqual(events[1].event_type, FinancialEvent.EventType.INVOICE_CANCELLED)

    def test_cannot_cancel_already_cancelled_invoice(self):
        InvoiceService.cancel(self.invoice, actor=self.user)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.cancel(self.invoice, actor=self.user)

    def test_cannot_mark_draft_as_sent(self):
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.mark_sent(self.invoice, actor=self.user)

    def test_mark_sent_on_issued_invoice(self):
        InvoiceService.issue(self.invoice, actor=self.user)
        invoice = InvoiceService.mark_sent(self.invoice, actor=self.user)
        self.assertEqual(invoice.status, Invoice.Status.SENT)
        self.assertIsNotNone(invoice.sent_at)
        # Sending doesn't affect revenue — no new FinancialEvent beyond
        # the original issue (Phase 2b's ledger-is-revenue-only decision).
        self.assertEqual(FinancialEvent.objects.filter(invoice=invoice).count(), 1)

    def test_can_still_cancel_a_sent_invoice_and_it_reverses_the_original_issue(self):
        InvoiceService.issue(self.invoice, actor=self.user)
        InvoiceService.mark_sent(self.invoice, actor=self.user)
        invoice = InvoiceService.cancel(self.invoice, actor=self.user)
        self.assertEqual(invoice.status, Invoice.Status.CANCELLED)
        events = list(FinancialEvent.objects.filter(invoice=invoice).order_by("id"))
        self.assertEqual(
            [e.event_type for e in events],
            [
                FinancialEvent.EventType.INVOICE_ISSUED,
                FinancialEvent.EventType.INVOICE_CANCELLED,
            ],
        )

    def test_cannot_edit_once_issued(self):
        InvoiceService.issue(self.invoice, actor=self.user)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.update_draft(self.invoice, notes="izmena")
