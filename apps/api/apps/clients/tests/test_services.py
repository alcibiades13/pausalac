from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.clients.services import ClientService
from apps.companies.models import Company
from apps.invoices.models import Invoice
from apps.invoices.services import InvoiceService
from apps.payments.services import PaymentService

DocumentType = Invoice.DocumentType


def _invoice(company, client_obj, document_type=DocumentType.INVOICE, price="1000.00"):
    today = timezone.now().date()
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        document_type=document_type,
        issue_date=today,
        due_date=today,
        service_date=today,
        notes="",
        line_items=[{"description": "X", "quantity": "1", "unit_price": price}],
    )


class ClientSummaryTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")

    def test_empty_client_has_zeroed_summary(self):
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["total_invoiced"], Decimal("0.00"))
        self.assertEqual(summary["total_paid"], Decimal("0.00"))
        self.assertEqual(summary["outstanding"], Decimal("0.00"))
        self.assertEqual(summary["invoice_count"], 0)
        self.assertIsNone(summary["last_invoice_date"])

    def test_draft_invoices_are_not_counted(self):
        _invoice(self.company, self.client_obj)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 0)
        self.assertEqual(summary["total_invoiced"], Decimal("0.00"))

    def test_cancelled_invoice_is_not_counted(self):
        invoice = _invoice(self.company, self.client_obj)
        InvoiceService.issue(invoice, actor=None)
        InvoiceService.cancel(invoice, actor=None)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 0)
        self.assertEqual(summary["total_invoiced"], Decimal("0.00"))

    def test_profaktura_is_not_counted(self):
        profaktura = _invoice(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=None)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 0)
        self.assertEqual(summary["total_invoiced"], Decimal("0.00"))

    def test_issued_invoice_counts_as_invoiced_but_not_paid(self):
        invoice = _invoice(self.company, self.client_obj)
        InvoiceService.issue(invoice, actor=None)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 1)
        self.assertEqual(summary["total_invoiced"], Decimal("1000.00"))
        self.assertEqual(summary["total_paid"], Decimal("0.00"))
        self.assertEqual(summary["outstanding"], Decimal("1000.00"))
        self.assertEqual(summary["last_invoice_date"], invoice.issue_date)

    def test_partial_and_full_payments_reduce_outstanding(self):
        invoice = _invoice(self.company, self.client_obj, price="1000.00")
        InvoiceService.issue(invoice, actor=None)
        PaymentService.record_payment(
            invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method="bank_transfer",
            notes="",
            actor=None,
        )
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["total_paid"], Decimal("400.00"))
        self.assertEqual(summary["outstanding"], Decimal("600.00"))

        PaymentService.record_payment(
            invoice,
            amount=Decimal("600.00"),
            paid_at=timezone.now().date(),
            method="bank_transfer",
            notes="",
            actor=None,
        )
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["total_paid"], Decimal("1000.00"))
        self.assertEqual(summary["outstanding"], Decimal("0.00"))

    def test_avans_counts_toward_invoiced_like_a_real_invoice(self):
        avans = _invoice(self.company, self.client_obj, DocumentType.ADVANCE, price="500.00")
        InvoiceService.issue(avans, actor=None)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 1)
        self.assertEqual(summary["total_invoiced"], Decimal("500.00"))

    def test_last_invoice_date_reflects_the_most_recent_issued_invoice(self):
        older = _invoice(self.company, self.client_obj)
        InvoiceService.issue(older, actor=None)
        newer = _invoice(self.company, self.client_obj)
        InvoiceService.issue(newer, actor=None)
        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["last_invoice_date"], newer.issue_date)

    def test_summary_is_scoped_to_the_given_client_only(self):
        other_client = Client.objects.create(company=self.company, name="Klijent B")
        other_invoice = _invoice(self.company, other_client, price="9999.00")
        InvoiceService.issue(other_invoice, actor=None)

        summary = ClientService.compute_summary(self.client_obj)
        self.assertEqual(summary["invoice_count"], 0)
        self.assertEqual(summary["total_invoiced"], Decimal("0.00"))
