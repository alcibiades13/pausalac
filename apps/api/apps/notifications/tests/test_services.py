from django.core import mail
from django.test import TestCase

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


class NotifyCompanyTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=self.owner, company=self.company, role=Membership.Role.OWNER)

    def _notify(self, priority=Notification.Priority.ATTENTION, dedup_key="test:1"):
        NotificationService.notify_company(
            self.company,
            event_type="test_event",
            dedup_key=dedup_key,
            priority=priority,
            title="Test naslov",
            message="Test poruka.",
            action_route="invoices",
        )

    def test_creates_in_app_notification_for_active_member(self):
        self._notify()
        notification = Notification.objects.get(recipient=self.owner, channel="in_app")
        self.assertEqual(notification.status, Notification.Status.SENT)
        self.assertIsNotNone(notification.sent_at)
        self.assertEqual(notification.title, "Test naslov")

    def test_attention_priority_creates_no_email_row(self):
        self._notify(priority=Notification.Priority.ATTENTION)
        self.assertFalse(
            Notification.objects.filter(recipient=self.owner, channel="email").exists()
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_critical_priority_creates_email_row_and_sends(self):
        self._notify(priority=Notification.Priority.CRITICAL)
        email_notification = Notification.objects.get(recipient=self.owner, channel="email")
        self.assertEqual(email_notification.status, Notification.Status.SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.owner.email])
        self.assertEqual(mail.outbox[0].subject, "Test naslov")

    def test_revoked_member_is_not_notified(self):
        revoked_user = User.objects.create_user(email="revoked@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=revoked_user, company=self.company, status=Membership.Status.REVOKED
        )
        self._notify()
        self.assertFalse(Notification.objects.filter(recipient=revoked_user).exists())

    def test_calling_twice_with_same_dedup_key_creates_no_duplicate(self):
        self._notify(dedup_key="dupe:1")
        self._notify(dedup_key="dupe:1")
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.owner, channel="in_app", dedup_key="dupe:1"
            ).count(),
            1,
        )

    def test_different_dedup_keys_create_separate_notifications(self):
        self._notify(dedup_key="a:1")
        self._notify(dedup_key="a:2")
        self.assertEqual(
            Notification.objects.filter(recipient=self.owner, channel="in_app").count(), 2
        )


class MarkReadTests(TestCase):
    def test_sets_read_at_once(self):
        company = Company.objects.create(name="Firma A", pib="123456789")
        owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=owner, company=company)
        notification = Notification.objects.create(
            company=company,
            recipient=owner,
            event_type="test_event",
            dedup_key="k1",
            priority=Notification.Priority.ATTENTION,
            channel=Notification.Channel.IN_APP,
            title="T",
            message="M",
        )
        self.assertIsNone(notification.read_at)
        NotificationService.mark_read(notification)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)
        first_read_at = notification.read_at

        NotificationService.mark_read(notification)
        notification.refresh_from_db()
        self.assertEqual(notification.read_at, first_read_at)
