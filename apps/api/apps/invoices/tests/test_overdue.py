from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import Invoice
from apps.invoices.services import InvoiceService


def _draft(company, client_obj, due_date):
    today = timezone.now().date()
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=due_date,
        service_date=today,
        notes="",
        line_items=[{"description": "X", "quantity": "1", "unit_price": "100"}],
    )


class MarkOverdueAllTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        self.today = timezone.now().date()
        self.past = self.today - timedelta(days=5)
        self.future = self.today + timedelta(days=5)

    def test_issued_invoice_past_due_date_becomes_overdue(self):
        invoice = InvoiceService.issue(_draft(self.company, self.client_obj, self.past), actor=None)
        count = InvoiceService.mark_overdue_all()
        invoice.refresh_from_db()
        self.assertEqual(count, 1)
        self.assertEqual(invoice.status, Invoice.Status.OVERDUE)

    def test_issued_invoice_not_yet_due_is_untouched(self):
        invoice = InvoiceService.issue(
            _draft(self.company, self.client_obj, self.future), actor=None
        )
        InvoiceService.mark_overdue_all()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)

    def test_draft_past_due_date_is_untouched(self):
        invoice = _draft(self.company, self.client_obj, self.past)
        InvoiceService.mark_overdue_all()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.DRAFT)

    def test_cancelled_invoice_past_due_date_is_untouched(self):
        invoice = InvoiceService.issue(_draft(self.company, self.client_obj, self.past), actor=None)
        invoice = InvoiceService.cancel(invoice, actor=None)
        InvoiceService.mark_overdue_all()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.CANCELLED)

    def test_overdue_invoice_can_still_be_cancelled(self):
        invoice = InvoiceService.issue(_draft(self.company, self.client_obj, self.past), actor=None)
        InvoiceService.mark_overdue_all()
        invoice.refresh_from_db()
        invoice = InvoiceService.cancel(invoice, actor=None)
        self.assertEqual(invoice.status, Invoice.Status.CANCELLED)
