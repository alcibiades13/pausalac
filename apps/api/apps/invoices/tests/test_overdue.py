from datetime import timedelta

from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership
from apps.invoices.models import Invoice
from apps.invoices.services import InvoiceService
from apps.notifications.models import Notification


def _draft(company, client_obj, due_date, price="100"):
    today = timezone.now().date()
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=due_date,
        service_date=today,
        notes="",
        line_items=[{"description": "X", "quantity": "1", "unit_price": price}],
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


class MarkOverdueAllNotificationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=self.owner, company=self.company)
        self.past = timezone.now().date() - timedelta(days=5)

    def test_creates_one_attention_in_app_notification_and_no_email(self):
        InvoiceService.issue(_draft(self.company, self.client_obj, self.past), actor=None)
        InvoiceService.mark_overdue_all()

        notifications = Notification.objects.filter(
            recipient=self.owner, event_type="invoice_overdue"
        )
        self.assertEqual(notifications.count(), 1)
        notification = notifications.get()
        self.assertEqual(notification.channel, Notification.Channel.IN_APP)
        self.assertEqual(notification.priority, Notification.Priority.ATTENTION)
        self.assertEqual(len(mail.outbox), 0)

    def test_running_sweep_twice_creates_no_duplicate(self):
        InvoiceService.issue(_draft(self.company, self.client_obj, self.past), actor=None)
        InvoiceService.mark_overdue_all()
        InvoiceService.mark_overdue_all()

        self.assertEqual(
            Notification.objects.filter(recipient=self.owner, event_type="invoice_overdue").count(),
            1,
        )


class PaymentReminderEmailTests(TestCase):
    """Master prompt §107 — the client-facing email distinct from the
    internal in-app notification tested above (docs/decisions-log.md's
    Phase 6 audit named this exact gap)."""

    def setUp(self):
        self.company = Company.objects.create(name="Firma A")
        self.past = timezone.now().date() - timedelta(days=5)

    def test_sends_a_reminder_to_the_client_when_an_email_is_on_file(self):
        client_obj = Client.objects.create(
            company=self.company, name="Klijent A", email="klijent@primer.rs"
        )
        invoice = InvoiceService.issue(
            _draft(self.company, client_obj, self.past, price="1500.00"), actor=None
        )
        InvoiceService.mark_overdue_all()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["klijent@primer.rs"])
        self.assertIn(invoice.invoice_number, mail.outbox[0].subject)

    def test_no_email_sent_when_the_client_has_no_email_on_file(self):
        client_obj = Client.objects.create(company=self.company, name="Klijent bez email-a")
        InvoiceService.issue(_draft(self.company, client_obj, self.past), actor=None)
        InvoiceService.mark_overdue_all()
        self.assertEqual(len(mail.outbox), 0)

    def test_reminder_is_also_sent_for_an_overdue_avans(self):
        # Avans behaves like a real invoice for the ledger (Phase 6c), and
        # a reminder email for it is sent too — it's a real financial
        # obligation from the client's perspective, same as an invoice.
        client_obj = Client.objects.create(
            company=self.company, name="Klijent A", email="klijent@primer.rs"
        )
        invoice = InvoiceService.create_draft(
            company=self.company,
            client=client_obj,
            document_type=Invoice.DocumentType.ADVANCE,
            issue_date=timezone.now().date(),
            due_date=self.past,
            service_date=timezone.now().date(),
            notes="",
            line_items=[{"description": "X", "quantity": "1", "unit_price": "100"}],
        )
        InvoiceService.issue(invoice, actor=None)
        InvoiceService.mark_overdue_all()
        self.assertEqual(len(mail.outbox), 1)
