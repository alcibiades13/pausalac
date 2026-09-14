from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry
from apps.companies.models import Company
from apps.notifications.models import Notification

from ..models import Subscription
from ..services import SubscriptionService
from ..testing import seed_test_plans


class GetOrCreateTrialTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="111111111")

    @override_settings(SUBSCRIPTION_TRIAL_DAYS=14)
    def test_creates_a_trialing_subscription(self):
        subscription = SubscriptionService.get_or_create_trial(self.company)
        self.assertEqual(subscription.status, Subscription.Status.TRIALING)
        self.assertIsNone(subscription.plan)
        days_out = (subscription.trial_ends_at - timezone.now()).days
        self.assertEqual(days_out, 13)  # 14 days minus rounding-down of the fractional day

    def test_is_idempotent(self):
        first = SubscriptionService.get_or_create_trial(self.company)
        second = SubscriptionService.get_or_create_trial(self.company)
        self.assertEqual(first.id, second.id)


class HasActiveAccessTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="222222222")

    def test_true_when_no_subscription_row_exists(self):
        self.assertTrue(SubscriptionService.has_active_access(self.company))

    def test_true_for_trialing_active_and_grace_period(self):
        for status in (
            Subscription.Status.TRIALING,
            Subscription.Status.ACTIVE,
            Subscription.Status.GRACE_PERIOD,
        ):
            with self.subTest(status=status):
                company = Company.objects.create(name=f"Firma {status}", pib=None)
                Subscription.objects.create(
                    company=company, status=status, trial_ends_at=timezone.now()
                )
                self.assertTrue(SubscriptionService.has_active_access(company))

    def test_false_for_cancelled_and_expired(self):
        for status in (Subscription.Status.CANCELLED, Subscription.Status.EXPIRED):
            with self.subTest(status=status):
                company = Company.objects.create(name=f"Firma {status}", pib=None)
                Subscription.objects.create(
                    company=company, status=status, trial_ends_at=timezone.now()
                )
                self.assertFalse(SubscriptionService.has_active_access(company))


class ActivatePlanTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="333333333")
        self.actor = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.plans = seed_test_plans()
        self.subscription = SubscriptionService.get_or_create_trial(self.company)

    def test_activates_and_snapshots_price(self):
        plan = self.plans["professional"]
        subscription = SubscriptionService.activate_plan(self.subscription, plan, actor=self.actor)
        self.assertEqual(subscription.status, Subscription.Status.ACTIVE)
        self.assertEqual(subscription.plan_id, plan.id)
        self.assertEqual(subscription.price_snapshot, plan.price)
        self.assertIsNotNone(subscription.current_period_end)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="subscription", entity_id=subscription.id, action="plan_activated"
            ).exists()
        )

    def test_reactivating_clears_previous_cancellation(self):
        SubscriptionService.cancel(self.subscription, actor=self.actor)
        subscription = SubscriptionService.activate_plan(
            self.subscription, self.plans["starter"], actor=self.actor
        )
        self.assertIsNone(subscription.cancelled_at)
        self.assertEqual(subscription.status, Subscription.Status.ACTIVE)


class CancelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="444444444")
        self.actor = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.subscription = SubscriptionService.get_or_create_trial(self.company)

    def test_cancel_sets_status_and_timestamp(self):
        subscription = SubscriptionService.cancel(self.subscription, actor=self.actor)
        self.assertEqual(subscription.status, Subscription.Status.CANCELLED)
        self.assertIsNotNone(subscription.cancelled_at)
        self.assertTrue(
            AuditLogEntry.objects.filter(
                entity_type="subscription", entity_id=subscription.id, action="cancelled"
            ).exists()
        )


class ExpireTrialsTests(TestCase):
    def test_flips_past_due_trials_and_notifies(self):
        company = Company.objects.create(name="Firma A", pib="555555555")
        owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        from apps.companies.models import Membership

        Membership.objects.create(user=owner, company=company)
        subscription = Subscription.objects.create(
            company=company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() - timedelta(days=1),
        )

        count = SubscriptionService.expire_trials()

        self.assertEqual(count, 1)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.Status.EXPIRED)
        self.assertTrue(
            Notification.objects.filter(recipient=owner, event_type="trial_expired").exists()
        )

    def test_does_not_touch_trials_not_yet_due(self):
        company = Company.objects.create(name="Firma A", pib="666666666")
        subscription = Subscription.objects.create(
            company=company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() + timedelta(days=5),
        )
        count = SubscriptionService.expire_trials()
        self.assertEqual(count, 0)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.Status.TRIALING)

    def test_second_run_is_a_no_op(self):
        company = Company.objects.create(name="Firma A", pib="777777777")
        Subscription.objects.create(
            company=company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() - timedelta(days=1),
        )
        SubscriptionService.expire_trials()
        self.assertEqual(SubscriptionService.expire_trials(), 0)


class SendTrialWarningsTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="888888888")
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        from apps.companies.models import Membership

        Membership.objects.create(user=self.owner, company=self.company)

    def test_warns_when_trial_ends_soon(self):
        subscription = Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() + timedelta(days=2),
        )
        count = SubscriptionService.send_trial_warnings()
        self.assertEqual(count, 1)
        subscription.refresh_from_db()
        self.assertIsNotNone(subscription.trial_warning_sent_at)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner, event_type="trial_ending_soon"
            ).exists()
        )

    def test_does_not_warn_twice(self):
        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() + timedelta(days=2),
        )
        SubscriptionService.send_trial_warnings()
        self.assertEqual(SubscriptionService.send_trial_warnings(), 0)

    def test_does_not_warn_when_trial_ends_far_out(self):
        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.TRIALING,
            trial_ends_at=timezone.now() + timedelta(days=10),
        )
        self.assertEqual(SubscriptionService.send_trial_warnings(), 0)

    def test_does_not_warn_non_trialing_subscriptions(self):
        Subscription.objects.create(
            company=self.company,
            status=Subscription.Status.ACTIVE,
            trial_ends_at=timezone.now() + timedelta(days=2),
        )
        self.assertEqual(SubscriptionService.send_trial_warnings(), 0)
