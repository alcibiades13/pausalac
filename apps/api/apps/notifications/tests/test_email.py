"""Master prompt §107 EMAIL SYSTEM — apps.notifications.email.EmailService."""

from django.core import mail
from django.test import TestCase

from apps.notifications.email import EmailService


class EmailServiceTests(TestCase):
    def test_send_renders_the_template_and_delivers_a_multipart_message(self):
        EmailService.send(
            "verification",
            {"link": "https://pausalac.rs/verifikacija?token=abc123"},
            to=["korisnik@primer.rs"],
            subject="Potvrdi email",
        )
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["korisnik@primer.rs"])
        self.assertEqual(message.subject, "Potvrdi email")
        # Plain-text alternative must actually contain the real link, not
        # just the button's visible label — strip_tags on <a href=...>
        # drops the href entirely, only the anchor text survives; the
        # template puts the raw link in visible text specifically so
        # plain-text clients (and this assertion) still get the URL.
        self.assertIn("https://pausalac.rs/verifikacija?token=abc123", message.body)
        # An HTML alternative is attached (multipart, not HTML-only body).
        self.assertEqual(len(message.alternatives), 1)
        html_body, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("https://pausalac.rs/verifikacija?token=abc123", html_body)

    def test_send_attaches_files_when_given(self):
        EmailService.send(
            "invoice_sent",
            {
                "invoice_number": "INV-2026-001",
                "company_name": "Firma A",
                "total_formatted": "1.000,00",
                "currency": "RSD",
                "message": "",
            },
            to=["klijent@primer.rs"],
            subject="Faktura INV-2026-001",
            attachments=[("INV-2026-001.pdf", b"%PDF-1.4 fake", "application/pdf")],
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        filename, content, mimetype = mail.outbox[0].attachments[0]
        self.assertEqual(filename, "INV-2026-001.pdf")
        self.assertEqual(mimetype, "application/pdf")

    def test_every_named_template_renders_without_error(self):
        # One test per template file, proving the seam is real (not a
        # stub) even for the three not wired to a send-trigger this phase.
        contexts = {
            "verification": {"link": "https://x/1"},
            "password_reset": {"link": "https://x/2"},
            "invoice_sent": {
                "invoice_number": "INV-2026-001",
                "company_name": "Firma",
                "total_formatted": "1,00",
                "currency": "RSD",
                "message": "",
            },
            "payment_reminder": {
                "invoice_number": "INV-2026-001",
                "company_name": "Firma",
                "total_formatted": "1,00",
                "currency": "RSD",
                "due_date": "01.01.2026.",
            },
            "payment_confirmation": {
                "invoice_number": "INV-2026-001",
                "company_name": "Firma",
                "total_formatted": "1,00",
                "currency": "RSD",
            },
            "obligation_reminder": {"period_start": "2026-01-01"},
            "trial": {
                "heading": "Probni period ističe",
                "body_text": "...",
                "subscription_url": "https://x/3",
            },
            "accountant_invitation": {"accounting_org_name": "Agencija d.o.o."},
        }
        for template_name, context in contexts.items():
            with self.subTest(template=template_name):
                mail.outbox.clear()
                EmailService.send(template_name, context, to=["x@primer.rs"], subject="Test")
                self.assertEqual(len(mail.outbox), 1)
