from datetime import date, timedelta
from decimal import Decimal

from django.core import mail
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.notifications.models import Notification
from apps.taxes.models import TaxObligation
from apps.taxes.services import TaxService
from apps.taxes.testing import seed_test_rates


class CreateResolutionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        seed_test_rates()

    def test_generates_one_obligation_per_month_full_year(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 12, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligations = TaxObligation.objects.filter(resolution=resolution).order_by("period_start")
        self.assertEqual(obligations.count(), 12)
        self.assertEqual(obligations.first().period_start, date(2026, 1, 1))
        self.assertEqual(obligations.last().period_start, date(2026, 12, 1))

    def test_generates_partial_range(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 3, 1),
            effective_until=date(2026, 5, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligations = list(
            TaxObligation.objects.filter(resolution=resolution).order_by("period_start")
        )
        self.assertEqual(len(obligations), 3)
        self.assertEqual(
            [o.period_start for o in obligations],
            [date(2026, 3, 1), date(2026, 4, 1), date(2026, 5, 1)],
        )

    def test_amounts_snapshotted_onto_each_obligation(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        self.assertEqual(obligation.income_tax_amount, Decimal("10000.00"))
        self.assertEqual(obligation.pio_amount, Decimal("24000.00"))
        self.assertEqual(obligation.health_amount, Decimal("10300.00"))
        self.assertEqual(obligation.unemployment_amount, Decimal("750.00"))
        self.assertEqual(obligation.total_amount, Decimal("45050.00"))

    def test_due_date_is_15th_of_following_month(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 3, 1),
            effective_until=date(2026, 3, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        self.assertEqual(obligation.due_date, date(2026, 4, 15))

    def test_overlapping_range_raises_validation_error(self):
        TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 6, 30),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        with self.assertRaises(ValidationError):
            TaxService.create_resolution(
                self.company,
                effective_from=date(2026, 6, 1),
                effective_until=date(2026, 12, 31),
                tax_base=Decimal("110000.00"),
                income_tax_amount=Decimal("11000.00"),
                pio_amount=Decimal("26400.00"),
                health_amount=Decimal("11330.00"),
                unemployment_amount=Decimal("825.00"),
            )


class RateCheckWarningsTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        seed_test_rates()

    def test_matching_amounts_produce_no_warnings(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        self.assertEqual(TaxService.rate_check_warnings(resolution), [])

    def test_mismatched_amount_produces_a_warning(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("50000.00"),  # way off from 10%
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        warnings = TaxService.rate_check_warnings(resolution)
        self.assertEqual(len(warnings), 1)
        self.assertIn("porez na prihod", warnings[0])

    def test_missing_rate_produces_a_graceful_warning_not_a_crash(self):
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=date(2019, 1, 1),  # before any seeded rate's effective_from
            effective_until=date(2019, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        warnings = TaxService.rate_check_warnings(resolution)
        self.assertEqual(len(warnings), 4)
        self.assertTrue(all("Ne može da se proveri" in w for w in warnings))


class MarkOverdueAllTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        seed_test_rates()

    def test_flips_only_pending_past_due_date(self):
        past_month = date(timezone.now().year - 1, 1, 1)
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=past_month,
            effective_until=past_month,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        self.assertEqual(obligation.status, TaxObligation.Status.PENDING)

        count = TaxService.mark_overdue_all()
        obligation.refresh_from_db()
        self.assertEqual(count, 1)
        self.assertEqual(obligation.status, TaxObligation.Status.OVERDUE)

    def test_future_obligation_untouched(self):
        future_month_start = (timezone.now().date().replace(day=1) + timedelta(days=60)).replace(
            day=1
        )
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=future_month_start,
            effective_until=future_month_start,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        TaxService.mark_overdue_all()
        obligation.refresh_from_db()
        self.assertEqual(obligation.status, TaxObligation.Status.PENDING)

    def test_paid_obligation_untouched(self):
        past_month = date(timezone.now().year - 1, 1, 1)
        resolution = TaxService.create_resolution(
            self.company,
            effective_from=past_month,
            effective_until=past_month,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        TaxService.mark_paid(obligation, actor=None)
        TaxService.mark_overdue_all()
        obligation.refresh_from_db()
        self.assertEqual(obligation.status, TaxObligation.Status.PAID)


class MarkPaidTests(TestCase):
    def test_sets_status_and_paid_at(self):
        company = Company.objects.create(name="Firma A", pib="123456789")
        seed_test_rates()
        resolution = TaxService.create_resolution(
            company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        obligation = TaxObligation.objects.get(resolution=resolution)
        self.assertIsNone(obligation.paid_at)

        TaxService.mark_paid(obligation, actor=None)
        obligation.refresh_from_db()
        self.assertEqual(obligation.status, TaxObligation.Status.PAID)
        self.assertIsNotNone(obligation.paid_at)


class MarkOverdueAllNotificationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=self.owner, company=self.company)
        seed_test_rates()
        self.past_month = date(timezone.now().year - 1, 1, 1)

    def _issue_past_due_obligation(self):
        TaxService.create_resolution(
            self.company,
            effective_from=self.past_month,
            effective_until=self.past_month,
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )

    def test_creates_critical_in_app_and_email_notification(self):
        self._issue_past_due_obligation()
        TaxService.mark_overdue_all()

        notifications = Notification.objects.filter(
            recipient=self.owner, event_type="tax_obligation_overdue"
        )
        self.assertEqual(notifications.count(), 2)
        channels = set(notifications.values_list("channel", flat=True))
        self.assertEqual(channels, {Notification.Channel.IN_APP, Notification.Channel.EMAIL})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Poreska obaveza kasni")

    def test_running_sweep_twice_creates_no_duplicate(self):
        self._issue_past_due_obligation()
        TaxService.mark_overdue_all()
        TaxService.mark_overdue_all()

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.owner, event_type="tax_obligation_overdue"
            ).count(),
            2,
        )
        self.assertEqual(len(mail.outbox), 1)
