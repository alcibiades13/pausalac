"""
Phase 6c: Profaktura (non-binding, zero ledger impact) and Avans (behaves
exactly like a real Invoice — user-confirmed design decision, see
docs/decisions-log.md). Neither document type is specified anywhere in
either canonical spec document beyond a bare quick-create menu label.
"""

import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import FinancialEvent, Invoice
from apps.invoices.numbering import assign_invoice_number
from apps.invoices.services import InvalidTransitionError, InvoiceService
from apps.limits.models import RegulatoryRule
from apps.limits.services import LimitsService
from apps.payments.services import InvalidPaymentError, PaymentService

DocumentType = Invoice.DocumentType


def _make_company_client():
    company = Company.objects.create(name="Firma A", default_currency="RSD")
    client = Client.objects.create(company=company, name="Klijent A")
    return company, client


def _draft(company, client_obj, document_type=DocumentType.INVOICE, **overrides):
    today = timezone.now().date()
    fields = {
        "issue_date": today,
        "due_date": today,
        "service_date": today,
        "notes": "",
        "document_type": document_type,
        "line_items": [{"description": "Konsalting", "quantity": "1", "unit_price": "1000.00"}],
    }
    fields.update(overrides)
    return InvoiceService.create_draft(company=company, client=client_obj, **fields)


class DocumentTypeNumberingTests(TestCase):
    def test_each_document_type_has_its_own_prefix_and_counter(self):
        company, client_obj = _make_company_client()
        year = timezone.now().date().year

        invoice = assign_invoice_number(_draft(company, client_obj, DocumentType.INVOICE))
        profaktura = assign_invoice_number(_draft(company, client_obj, DocumentType.PROFORMA))
        avans = assign_invoice_number(_draft(company, client_obj, DocumentType.ADVANCE))
        second_invoice = assign_invoice_number(_draft(company, client_obj, DocumentType.INVOICE))

        self.assertEqual(invoice, f"INV-{year}-001")
        self.assertEqual(profaktura, f"PRO-{year}-001")
        self.assertEqual(avans, f"AVN-{year}-001")
        # A second real invoice continues its own sequence, unaffected by
        # the profaktura/avans numbers assigned in between.
        self.assertEqual(second_invoice, f"INV-{year}-002")


class ProfakturaLedgerTests(TestCase):
    def setUp(self):
        self.company, self.client_obj = _make_company_client()
        self.user = None

    def test_issuing_a_profaktura_creates_no_financial_event_or_kpo_entry(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)

        self.assertFalse(
            FinancialEvent.objects.filter(invoice=profaktura).exists(),
            "Profaktura must never create a FinancialEvent",
        )
        self.assertFalse(profaktura.kpo_entries.exists(), "Profaktura must never create a KPOEntry")

    def test_cancelling_an_issued_profaktura_creates_no_reversal_event(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)
        InvoiceService.cancel(profaktura, actor=self.user)

        self.assertFalse(FinancialEvent.objects.filter(invoice=profaktura).exists())

    def test_profaktura_is_excluded_from_the_overdue_sweep(self):
        past_due_date = datetime.date(2000, 1, 1)
        profaktura = _draft(
            self.company, self.client_obj, DocumentType.PROFORMA, due_date=past_due_date
        )
        InvoiceService.issue(profaktura, actor=self.user)

        InvoiceService.mark_overdue_all()

        profaktura.refresh_from_db()
        self.assertNotEqual(profaktura.status, Invoice.Status.OVERDUE)

    def test_payment_is_rejected_against_an_issued_profaktura(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)

        with self.assertRaises(InvalidPaymentError):
            PaymentService.record_payment(
                profaktura,
                amount=Decimal("1000.00"),
                paid_at=timezone.now().date(),
                method="bank_transfer",
                notes="",
                actor=self.user,
            )


class AvansLedgerTests(TestCase):
    def setUp(self):
        self.company, self.client_obj = _make_company_client()
        self.user = None

    def test_issuing_an_avans_creates_a_financial_event_and_kpo_entry_like_a_real_invoice(self):
        avans = _draft(self.company, self.client_obj, DocumentType.ADVANCE)
        InvoiceService.issue(avans, actor=self.user)

        self.assertTrue(FinancialEvent.objects.filter(invoice=avans).exists())
        self.assertTrue(avans.kpo_entries.exists())

    def test_avans_counts_toward_the_pausal_turnover_limit_but_profaktura_does_not(self):
        RegulatoryRule.objects.create(
            identifier="pausal_turnover_limit",
            config={"amount": "6000000", "currency": "RSD"},
            effective_from=datetime.date(2020, 1, 1),
            source="test",
        )
        avans = _draft(self.company, self.client_obj, DocumentType.ADVANCE)
        InvoiceService.issue(avans, actor=self.user)

        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)

        tracker = LimitsService.compute_pausal_limit(self.company)
        # Only the avans's 1000.00 should be reflected — the profaktura's
        # own 1000.00 must not appear at all.
        self.assertEqual(tracker["current"], Decimal("1000.00"))

    def test_avans_can_receive_a_payment_like_a_real_invoice(self):
        avans = _draft(self.company, self.client_obj, DocumentType.ADVANCE)
        InvoiceService.issue(avans, actor=self.user)

        payment = PaymentService.record_payment(
            avans,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method="bank_transfer",
            notes="",
            actor=self.user,
        )
        avans.refresh_from_db()
        self.assertEqual(payment.amount, Decimal("1000.00"))
        self.assertEqual(avans.status, Invoice.Status.PAID)

    def test_avans_is_included_in_the_overdue_sweep_unlike_profaktura(self):
        past_due_date = datetime.date(2000, 1, 1)
        avans = _draft(self.company, self.client_obj, DocumentType.ADVANCE, due_date=past_due_date)
        InvoiceService.issue(avans, actor=self.user)

        InvoiceService.mark_overdue_all()

        avans.refresh_from_db()
        self.assertEqual(avans.status, Invoice.Status.OVERDUE)


class ConvertProfakturaToInvoiceTests(TestCase):
    def setUp(self):
        self.company, self.client_obj = _make_company_client()
        self.user = None

    def test_converting_an_issued_profaktura_creates_a_linked_draft_invoice(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)

        invoice = InvoiceService.convert_to_invoice(profaktura, actor=self.user)

        self.assertEqual(invoice.document_type, DocumentType.INVOICE)
        self.assertEqual(invoice.status, Invoice.Status.DRAFT)
        self.assertEqual(invoice.converted_from_id, profaktura.id)
        self.assertEqual(invoice.client_id, profaktura.client_id)
        self.assertEqual(invoice.total, profaktura.total)
        self.assertEqual(invoice.items.count(), profaktura.items.count())
        # The profaktura itself is untouched — still issued, not consumed.
        profaktura.refresh_from_db()
        self.assertEqual(profaktura.status, Invoice.Status.ISSUED)

    def test_converting_a_sent_profaktura_is_allowed(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)
        InvoiceService.mark_sent(profaktura, actor=self.user)

        invoice = InvoiceService.convert_to_invoice(profaktura, actor=self.user)
        self.assertEqual(invoice.converted_from_id, profaktura.id)

    def test_converting_a_draft_profaktura_is_rejected(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.convert_to_invoice(profaktura, actor=self.user)

    def test_converting_a_cancelled_profaktura_is_rejected(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)
        InvoiceService.cancel(profaktura, actor=self.user)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.convert_to_invoice(profaktura, actor=self.user)

    def test_converting_a_regular_invoice_is_rejected(self):
        invoice = _draft(self.company, self.client_obj, DocumentType.INVOICE)
        InvoiceService.issue(invoice, actor=self.user)
        with self.assertRaises(InvalidTransitionError):
            InvoiceService.convert_to_invoice(invoice, actor=self.user)

    def test_converting_an_already_converted_profaktura_is_rejected(self):
        profaktura = _draft(self.company, self.client_obj, DocumentType.PROFORMA)
        InvoiceService.issue(profaktura, actor=self.user)
        InvoiceService.convert_to_invoice(profaktura, actor=self.user)

        with self.assertRaises(InvalidTransitionError):
            InvoiceService.convert_to_invoice(profaktura, actor=self.user)


class DocumentTypeImmutabilityTests(TestCase):
    def test_update_draft_does_not_reject_document_type_but_service_layer_has_no_own_guard(self):
        """
        The immutability guard lives in the serializer's validate() (API
        boundary), not in InvoiceService.update_draft itself — this test
        documents that update_draft alone will happily change it if called
        directly, so the serializer-level test (test_views.py) is the one
        that actually proves the real protection users get through the API.
        """
        company, client_obj = _make_company_client()
        profaktura = _draft(company, client_obj, DocumentType.PROFORMA)
        InvoiceService.update_draft(profaktura, document_type=DocumentType.INVOICE)
        profaktura.refresh_from_db()
        self.assertEqual(profaktura.document_type, DocumentType.INVOICE)
