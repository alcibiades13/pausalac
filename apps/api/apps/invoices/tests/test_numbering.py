import threading

from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.companies.models import Company
from apps.invoices.models import Invoice
from apps.invoices.numbering import assign_invoice_number
from apps.invoices.services import InvoiceService


def _draft(company, client_obj):
    today = timezone.now().date()
    return InvoiceService.create_draft(
        company=company,
        client=client_obj,
        issue_date=today,
        due_date=today,
        service_date=today,
        notes="",
        line_items=[{"description": "X", "quantity": "1", "unit_price": "100"}],
    )


class InvoiceNumberingFormatTests(TransactionTestCase):
    # TransactionTestCase flushes every table after each test (not just
    # ones it touched), which would silently wipe migration-seeded
    # reference data (apps.limits.RegulatoryRule, added Phase 3a) for
    # the rest of the test session. serialized_rollback restores the
    # post-migration snapshot after each flush instead of leaving it empty.
    serialized_rollback = True

    def test_format_is_inv_year_seq(self):
        company = Company.objects.create(name="Firma A")
        client_obj = Client.objects.create(company=company, name="Klijent A")
        invoice = _draft(company, client_obj)
        number = assign_invoice_number(invoice)
        year = timezone.now().date().year
        self.assertEqual(number, f"INV-{year}-001")

    def test_sequence_increments_and_is_per_company(self):
        company_a = Company.objects.create(name="Firma A")
        company_b = Company.objects.create(name="Firma B")
        client_a = Client.objects.create(company=company_a, name="Klijent A")
        client_b = Client.objects.create(company=company_b, name="Klijent B")

        first = assign_invoice_number(_draft(company_a, client_a))
        second = assign_invoice_number(_draft(company_a, client_a))
        other_company_first = assign_invoice_number(_draft(company_b, client_b))

        year = timezone.now().date().year
        self.assertEqual(first, f"INV-{year}-001")
        self.assertEqual(second, f"INV-{year}-002")
        # A different company's sequence starts over at 001, independently.
        self.assertEqual(other_company_first, f"INV-{year}-001")


class InvoiceNumberingConcurrencyTests(TransactionTestCase):
    """
    Master prompt §95: concurrent invoice creation must not produce
    duplicate numbers. Best-effort against SQLite in this sandbox (no
    Postgres available here) — the select_for_update + get_or_create
    pattern is the standard Django-documented approach, but this is worth
    re-confirming against the real Postgres compose service too.
    """

    # See InvoiceNumberingFormatTests above for why this is needed.
    serialized_rollback = True

    def test_concurrent_number_assignment_produces_no_duplicates(self):
        company = Company.objects.create(name="Firma A")
        client_obj = Client.objects.create(company=company, name="Klijent A")
        invoices = [_draft(company, client_obj) for _ in range(8)]

        results: list[str] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def worker(invoice_id: int) -> None:
            try:
                close_old_connections()
                invoice = Invoice.objects.get(pk=invoice_id)
                number = assign_invoice_number(invoice)
                with lock:
                    results.append(number)
            except Exception as exc:  # noqa: BLE001 - captured for the assertion below
                with lock:
                    errors.append(exc)
            finally:
                close_old_connections()

        threads = [threading.Thread(target=worker, args=(inv.id,)) for inv in invoices]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), len(set(results)), f"duplicate invoice numbers: {results}")
        self.assertEqual(len(results), 8)
