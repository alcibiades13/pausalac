from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import FinancialEvent, Invoice
from apps.invoices.services import InvoiceService
from apps.limits.services import LimitsService
from apps.limits.testing import seed_test_rules
from apps.payments.services import PaymentService


def _issued_invoice(company, client_obj, *, unit_price, issue_date=None):
    issue_date = issue_date or timezone.now().date()
    invoice = InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=issue_date,
        due_date=issue_date,
        service_date=issue_date,
        notes="",
        line_items=[{"description": "Usluga", "quantity": "1", "unit_price": unit_price}],
    )
    return InvoiceService.issue(invoice, actor=None)


class LimitsServiceTests(TestCase):
    def setUp(self):
        seed_test_rules()
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")
        self.today = timezone.now().date()

    def test_pausal_limit_calendar_year_percentage(self):
        _issued_invoice(self.company, self.client_obj, unit_price="2840000.00")
        tracker = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        self.assertEqual(tracker["current"], Decimal("2840000.00"))
        self.assertEqual(tracker["threshold"], Decimal("6000000.00"))
        self.assertEqual(tracker["percentage"], 47)
        self.assertEqual(tracker["remaining"], Decimal("3160000.00"))
        self.assertEqual(tracker["period"]["type"], "calendar_year")

    def test_invoice_outside_calendar_year_excluded_from_pausal_limit(self):
        last_year = date(self.today.year - 1, 6, 1)
        invoice = _issued_invoice(
            self.company, self.client_obj, unit_price="500000.00", issue_date=last_year
        )
        # occurred_at is auto_now_add (recorded-now), so backdate it directly
        # to simulate an event that actually happened last calendar year.
        FinancialEvent.objects.filter(invoice=invoice).update(
            occurred_at=timezone.make_aware(timezone.datetime(last_year.year, 6, 1))
        )
        tracker = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        self.assertEqual(tracker["current"], Decimal("0.00"))

    def test_vat_threshold_trailing_12_months_independent_of_calendar_year(self):
        thirteen_months_ago = self.today - timedelta(days=395)
        invoice = _issued_invoice(
            self.company, self.client_obj, unit_price="1000000.00", issue_date=thirteen_months_ago
        )
        FinancialEvent.objects.filter(invoice=invoice).update(
            occurred_at=timezone.make_aware(
                timezone.datetime(
                    thirteen_months_ago.year, thirteen_months_ago.month, thirteen_months_ago.day
                )
            )
        )
        tracker = LimitsService.compute_vat_threshold(self.company, as_of=self.today)
        self.assertEqual(tracker["current"], Decimal("0.00"))
        self.assertEqual(tracker["period"]["type"], "trailing_12_months")

    def test_cancellation_nets_out_of_both_limits(self):
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="1000000.00")
        InvoiceService.cancel(invoice, actor=None)
        pausal = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        vat = LimitsService.compute_vat_threshold(self.company, as_of=self.today)
        self.assertEqual(pausal["current"], Decimal("0.00"))
        self.assertEqual(vat["current"], Decimal("0.00"))

    def test_payment_does_not_change_either_limit(self):
        """Promet/accrual basis, not cash — regression test for the
        2026-09-14-resolved cash-vs-accrual question."""
        invoice = _issued_invoice(self.company, self.client_obj, unit_price="1000000.00")
        before_pausal = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        PaymentService.record_payment(
            invoice,
            amount=Decimal("1000000.00"),
            paid_at=self.today,
            method="bank_transfer",
            notes="",
            actor=None,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.PAID)
        after_pausal = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        after_vat = LimitsService.compute_vat_threshold(self.company, as_of=self.today)
        self.assertEqual(before_pausal["current"], after_pausal["current"])
        self.assertEqual(after_pausal["current"], Decimal("1000000.00"))
        self.assertEqual(after_vat["current"], Decimal("1000000.00"))

    def test_warning_level_boundaries(self):
        cases = [
            (Decimal("4139999.99"), "ok"),  # 68.99% -> ok
            (Decimal("4200000.00"), "attention"),  # 70%
            (Decimal("5100000.00"), "warning"),  # 85%
            (Decimal("5700000.00"), "critical"),  # 95%
        ]
        for amount, expected_level in cases:
            with self.subTest(amount=amount):
                company = Company.objects.create(name=f"Firma {amount}", pib=f"{amount:.0f}"[:15])
                client_obj = Client.objects.create(company=company, name="Klijent")
                _issued_invoice(company, client_obj, unit_price=str(amount))
                tracker = LimitsService.compute_pausal_limit(company, as_of=self.today)
                self.assertEqual(tracker["warning_level"], expected_level)

    def test_projection_present_after_min_days_elapsed_absent_before(self):
        year_start = date(self.today.year, 1, 1)
        _issued_invoice(
            self.company, self.client_obj, unit_price="100000.00", issue_date=year_start
        )
        FinancialEvent.objects.update(
            occurred_at=timezone.make_aware(timezone.datetime(year_start.year, 1, 1))
        )

        early = LimitsService.compute_pausal_limit(self.company, as_of=date(year_start.year, 1, 3))
        self.assertIsNone(early["projection"])

        later = LimitsService.compute_pausal_limit(self.company, as_of=date(year_start.year, 1, 10))
        self.assertIsNotNone(later["projection"])
        self.assertEqual(later["projection"]["label"], "procena")

    def test_vat_threshold_never_has_projection(self):
        tracker = LimitsService.compute_vat_threshold(self.company, as_of=self.today)
        self.assertIsNone(tracker["projection"])

    def test_simulate_does_not_write_to_database(self):
        _issued_invoice(self.company, self.client_obj, unit_price="1000000.00")
        event_count_before = FinancialEvent.objects.count()
        invoice_count_before = Invoice.objects.count()

        result = LimitsService.simulate(self.company, Decimal("800000.00"), as_of=self.today)

        self.assertEqual(FinancialEvent.objects.count(), event_count_before)
        self.assertEqual(Invoice.objects.count(), invoice_count_before)
        self.assertEqual(result["before"]["pausal_limit"]["current"], Decimal("1000000.00"))
        self.assertEqual(result["after"]["pausal_limit"]["current"], Decimal("1800000.00"))
        self.assertEqual(
            result["after"]["pausal_limit"]["remaining"],
            result["before"]["pausal_limit"]["remaining"] - Decimal("800000.00"),
        )

    def test_tenant_isolation(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        other_client = Client.objects.create(company=other_company, name="Klijent B")
        _issued_invoice(other_company, other_client, unit_price="5000000.00")

        tracker = LimitsService.compute_pausal_limit(self.company, as_of=self.today)
        self.assertEqual(tracker["current"], Decimal("0.00"))


class LimitsHistoryTests(TestCase):
    """`compute_pausal_limit_history` — LimitProgressChart's data source."""

    def setUp(self):
        seed_test_rules()
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.client_obj = Client.objects.create(company=self.company, name="Klijent A")

    def test_history_is_cumulative_and_zero_filled(self):
        jan = _issued_invoice(self.company, self.client_obj, unit_price="100000.00", issue_date=date(2026, 1, 10))
        FinancialEvent.objects.filter(invoice=jan).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 1, 10))
        )
        mar = _issued_invoice(self.company, self.client_obj, unit_price="50000.00", issue_date=date(2026, 3, 5))
        FinancialEvent.objects.filter(invoice=mar).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 3, 5))
        )

        result = LimitsService.compute_pausal_limit_history(
            self.company, 2026, as_of=date(2026, 3, 31)
        )
        self.assertEqual(result["threshold"], Decimal("6000000.00"))
        history_by_month = {row["month"]: row["cumulative"] for row in result["history"]}
        self.assertEqual(history_by_month["2026-01-01"], Decimal("100000.00"))
        self.assertEqual(history_by_month["2026-02-01"], Decimal("100000.00"))  # carried forward, no new activity
        self.assertEqual(history_by_month["2026-03-01"], Decimal("150000.00"))

    def test_projection_continues_from_the_last_real_point(self):
        invoice = _issued_invoice(
            self.company, self.client_obj, unit_price="600000.00", issue_date=date(2026, 1, 10)
        )
        FinancialEvent.objects.filter(invoice=invoice).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 1, 10))
        )
        result = LimitsService.compute_pausal_limit_history(self.company, 2026, as_of=date(2026, 1, 20))
        self.assertTrue(result["projection"])
        # First projection point is exactly where history leaves off — no
        # visible jump/kink where the two lines are meant to meet.
        self.assertEqual(result["projection"][0]["month"], result["history"][-1]["month"])
        self.assertEqual(result["projection"][0]["cumulative"], result["history"][-1]["cumulative"])
        # Later projected months keep climbing toward the year-end estimate.
        self.assertGreater(result["projection"][-1]["cumulative"], result["projection"][0]["cumulative"])

    def test_no_projection_before_minimum_days_elapsed(self):
        result = LimitsService.compute_pausal_limit_history(self.company, 2026, as_of=date(2026, 1, 3))
        self.assertEqual(result["projection"], [])

    def test_past_year_has_no_projection(self):
        result = LimitsService.compute_pausal_limit_history(
            self.company, 2020, as_of=date(2026, 6, 1)
        )
        self.assertEqual(result["projection"], [])
        self.assertEqual(len(result["history"]), 12)

    def test_negative_month_from_cancellation_is_reflected(self):
        invoice = _issued_invoice(
            self.company, self.client_obj, unit_price="300000.00", issue_date=date(2026, 2, 1)
        )
        FinancialEvent.objects.filter(invoice=invoice).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 2, 1))
        )
        invoice2 = _issued_invoice(
            self.company, self.client_obj, unit_price="100000.00", issue_date=date(2026, 3, 1)
        )
        FinancialEvent.objects.filter(invoice=invoice2).update(
            occurred_at=timezone.make_aware(timezone.datetime(2026, 3, 1))
        )
        InvoiceService.cancel(invoice2, actor=None)
        FinancialEvent.objects.filter(
            invoice=invoice2, event_type=FinancialEvent.EventType.INVOICE_CANCELLED
        ).update(occurred_at=timezone.make_aware(timezone.datetime(2026, 3, 2)))

        result = LimitsService.compute_pausal_limit_history(
            self.company, 2026, as_of=date(2026, 3, 31)
        )
        history_by_month = {row["month"]: row["cumulative"] for row in result["history"]}
        # March's own net activity is -100000 + 100000 = 0, so cumulative
        # stays at February's 300000 rather than climbing further.
        self.assertEqual(history_by_month["2026-03-01"], Decimal("300000.00"))
