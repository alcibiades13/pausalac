from django.core import mail
from django.test import TestCase

from apps.accounts.models import User
from apps.companies.models import Company
from apps.notifications.models import Notification
from apps.notifications.tasks import send_notification_email_task


class SendNotificationEmailTaskTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.notification = Notification.objects.create(
            company=self.company,
            recipient=self.user,
            event_type="test_event",
            dedup_key="k1",
            priority=Notification.Priority.CRITICAL,
            channel=Notification.Channel.EMAIL,
            title="Naslov",
            message="Poruka.",
        )

    def test_sends_email_and_marks_sent(self):
        send_notification_email_task(self.notification.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@pausalac.rs"])
        self.assertEqual(mail.outbox[0].subject, "Naslov")
        self.assertEqual(mail.outbox[0].body, "Poruka.")

        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, Notification.Status.SENT)
        self.assertIsNotNone(self.notification.sent_at)

    def test_missing_notification_does_not_raise(self):
        send_notification_email_task(999999)
        self.assertEqual(len(mail.outbox), 0)
