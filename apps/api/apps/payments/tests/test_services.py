from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import FinancialEvent, Invoice
from apps.invoices.services import InvoiceService
from apps.payments.models import Payment
from apps.payments.services import InvalidPaymentError, PaymentService


def _issued_invoice(total_unit_price="1000.00"):
    company = Company.objects.create(name="Firma A")
    client_obj = Client.objects.create(company=company, name="Klijent A")
    user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
    today = timezone.now().date()
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=today,
        service_date=today,
        notes="",
        line_items=[{"description": "Usluga", "quantity": "1", "unit_price": total_unit_price}],
    )
    invoice = InvoiceService.issue(invoice, actor=user)
    return invoice, user


class RecordPaymentTests(TestCase):
    def setUp(self):
        self.invoice, self.user = _issued_invoice()

    def test_full_payment_marks_invoice_paid(self):
        payment = PaymentService.record_payment(
            self.invoice,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
            notes="",
            actor=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)
        self.assertIsNotNone(self.invoice.paid_at)
        self.assertEqual(payment.amount, Decimal("1000.00"))

    def test_partial_payment_marks_invoice_partially_paid(self):
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PARTIALLY_PAID)
        self.assertIsNone(self.invoice.paid_at)

    def test_two_partial_payments_add_up_to_paid(self):
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
        )
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("600.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)
        self.assertEqual(Payment.objects.filter(invoice=self.invoice).count(), 2)

    def test_each_payment_creates_exactly_one_financial_event_with_its_own_amount(self):
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
        )
        events = FinancialEvent.objects.filter(invoice=self.invoice).order_by("id")
        # [0] is the original INVOICE_ISSUED event from _issued_invoice().
        self.assertEqual(len(events), 2)
        self.assertEqual(events[1].event_type, FinancialEvent.EventType.INVOICE_PARTIALLY_PAID)
        self.assertEqual(
            events[1].amount, Decimal("400.00")
        )  # this payment's amount, not the total

    def test_cannot_pay_a_draft_invoice(self):
        company = Company.objects.create(name="Firma B")
        client_obj = Client.objects.create(company=company, name="Klijent B")
        draft = InvoiceService.create_draft(
            company=company,
            client=client_obj,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            service_date=timezone.now().date(),
            notes="",
            line_items=[{"description": "X", "quantity": "1", "unit_price": "1"}],
        )
        with self.assertRaises(InvalidPaymentError):
            PaymentService.record_payment(
                draft,
                amount=Decimal("1"),
                paid_at=timezone.now().date(),
                method=Payment.Method.CASH,
                notes="",
                actor=self.user,
            )

    def test_cannot_pay_a_cancelled_invoice(self):
        InvoiceService.cancel(self.invoice, actor=self.user)
        with self.assertRaises(InvalidPaymentError):
            PaymentService.record_payment(
                self.invoice,
                amount=Decimal("1"),
                paid_at=timezone.now().date(),
                method=Payment.Method.CASH,
                notes="",
                actor=self.user,
            )

    def test_amount_must_be_positive(self):
        with self.assertRaises(InvalidPaymentError):
            PaymentService.record_payment(
                self.invoice,
                amount=Decimal("0"),
                paid_at=timezone.now().date(),
                method=Payment.Method.CASH,
                notes="",
                actor=self.user,
            )

    def test_idempotency_key_replay_does_not_double_count(self):
        key = "test-key-123"
        first = PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
            idempotency_key=key,
        )
        second = PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.CASH,
            notes="",
            actor=self.user,
            idempotency_key=key,
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(Payment.objects.filter(invoice=self.invoice).count(), 1)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PARTIALLY_PAID)

    def test_payment_can_be_recorded_on_an_overdue_invoice(self):
        self.invoice.due_date = timezone.now().date() - timezone.timedelta(days=5)
        self.invoice.save(update_fields=["due_date"])
        InvoiceService.mark_overdue_all()
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.OVERDUE)

        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
            notes="",
            actor=self.user,
        )
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)


class PaymentConfirmationEmailTests(TestCase):
    """Master prompt §107 — sent to the client only on the transition to
    fully PAID, never on a partial payment."""

    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(
            company=self.company, name="Klijent A", email="klijent@primer.rs"
        )
        self.user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
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
        self.invoice = InvoiceService.issue(self.invoice, actor=self.user)

    def test_full_payment_sends_a_confirmation_to_the_client(self):
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
            notes="",
            actor=self.user,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["klijent@primer.rs"])
        self.assertIn(self.invoice.invoice_number, mail.outbox[0].subject)

    def test_partial_payment_sends_no_confirmation(self):
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("400.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
            notes="",
            actor=self.user,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_no_confirmation_when_the_client_has_no_email_on_file(self):
        self.client_obj.email = ""
        self.client_obj.save(update_fields=["email"])
        PaymentService.record_payment(
            self.invoice,
            amount=Decimal("1000.00"),
            paid_at=timezone.now().date(),
            method=Payment.Method.BANK_TRANSFER,
            notes="",
            actor=self.user,
        )
        self.assertEqual(len(mail.outbox), 0)
