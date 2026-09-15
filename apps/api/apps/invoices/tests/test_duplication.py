"""Master prompt §94: "When previous invoice exists: allow duplication." """

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import Invoice
from apps.invoices.services import InvoiceService

DocumentType = Invoice.DocumentType


def _make_company_client():
    company = Company.objects.create(name="Firma A", default_currency="RSD")
    client = Client.objects.create(company=company, name="Klijent A")
    return company, client


def _draft(company, client_obj, document_type=DocumentType.INVOICE):
    today = timezone.now().date()
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        document_type=document_type,
        issue_date=today,
        due_date=today,
        service_date=today,
        notes="Originalna napomena",
        line_items=[
            {"description": "Konsalting", "quantity": "2", "unit_price": "500.00"},
            {"description": "Dizajn", "quantity": "1", "unit_price": "300.00"},
        ],
    )


class DuplicateInvoiceTests(TestCase):
    def setUp(self):
        self.company, self.client_obj = _make_company_client()
        self.user = None

    def test_duplicating_a_draft_creates_an_independent_draft_copy(self):
        source = _draft(self.company, self.client_obj)
        duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)

        self.assertNotEqual(duplicate.id, source.id)
        self.assertEqual(duplicate.status, Invoice.Status.DRAFT)
        self.assertEqual(duplicate.client_id, source.client_id)
        self.assertEqual(duplicate.total, source.total)
        self.assertEqual(duplicate.notes, source.notes)
        self.assertEqual(duplicate.items.count(), source.items.count())
        self.assertIsNone(duplicate.invoice_number)

    def test_duplicating_an_issued_invoice_is_allowed_unlike_conversion(self):
        source = _draft(self.company, self.client_obj)
        InvoiceService.issue(source, actor=self.user)
        duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)
        self.assertEqual(duplicate.status, Invoice.Status.DRAFT)

    def test_duplicating_a_cancelled_invoice_is_allowed(self):
        source = _draft(self.company, self.client_obj)
        InvoiceService.issue(source, actor=self.user)
        InvoiceService.cancel(source, actor=self.user)
        duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)
        self.assertEqual(duplicate.status, Invoice.Status.DRAFT)

    def test_duplicate_preserves_the_source_document_type(self):
        for document_type in (DocumentType.INVOICE, DocumentType.PROFORMA, DocumentType.ADVANCE):
            with self.subTest(document_type=document_type):
                source = _draft(self.company, self.client_obj, document_type)
                duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)
                self.assertEqual(duplicate.document_type, document_type)

    def test_duplicate_has_no_converted_from_link(self):
        source = _draft(self.company, self.client_obj)
        duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)
        self.assertIsNone(duplicate.converted_from_id)

    def test_duplicate_can_be_created_more_than_once(self):
        source = _draft(self.company, self.client_obj)
        InvoiceService.issue(source, actor=self.user)
        first = InvoiceService.duplicate_invoice(source, actor=self.user)
        second = InvoiceService.duplicate_invoice(source, actor=self.user)
        self.assertNotEqual(first.id, second.id)

    def test_duplicate_dates_reset_to_today(self):
        source = _draft(self.company, self.client_obj)
        duplicate = InvoiceService.duplicate_invoice(source, actor=self.user)
        today = timezone.now().date()
        self.assertEqual(duplicate.issue_date, today)
        self.assertEqual(duplicate.service_date, today)
