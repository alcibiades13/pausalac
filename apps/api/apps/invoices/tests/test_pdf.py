from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.pdf import format_money, render_invoice_pdf
from apps.invoices.services import InvoiceService


class RenderInvoicePdfTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Firma A", pib="123456789", bank_account="RS35...1234"
        )
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        today = timezone.now().date()
        self.invoice = InvoiceService.create_draft(
            company=self.company,
            client=self.client_obj,
            issue_date=today,
            due_date=today,
            service_date=today,
            notes="Hvala na saradnji.",
            line_items=[{"description": "Konsalting", "quantity": "2", "unit_price": "1500.00"}],
        )

    def test_renders_valid_pdf_for_a_draft(self):
        pdf_bytes = render_invoice_pdf(self.invoice)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_renders_valid_pdf_for_an_issued_invoice(self):
        invoice = InvoiceService.issue(self.invoice, actor=None)
        pdf_bytes = render_invoice_pdf(invoice)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


class FormatMoneyTests(TestCase):
    def test_uses_serbian_thousands_and_decimal_separators(self):
        from decimal import Decimal

        self.assertEqual(format_money(Decimal("2840000")), "2.840.000,00")
        self.assertEqual(format_money(Decimal("1500.5")), "1.500,50")
