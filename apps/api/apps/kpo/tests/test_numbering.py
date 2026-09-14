import threading

from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from apps.companies.models import Company
from apps.kpo.numbering import assign_sequence_number


class KPONumberingConcurrencyTests(TransactionTestCase):
    """
    Mirrors apps.invoices.tests.test_numbering's concurrency test (master
    prompt §95). serialized_rollback=True is set from the start here —
    Phase 3a's incident (a TransactionTestCase silently flushing
    migration-seeded RegulatoryRule rows for the rest of a --reuse-db
    session) is exactly what this guards against for any other test that
    later runs in the same session.
    """

    serialized_rollback = True

    def test_concurrent_sequence_assignment_produces_no_duplicates(self):
        company = Company.objects.create(name="Firma A")
        entry_date = timezone.now().date()

        results: list[int] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def worker() -> None:
            try:
                close_old_connections()
                number = assign_sequence_number(entry_date, company)
                with lock:
                    results.append(number)
            except Exception as exc:  # noqa: BLE001 - captured for the assertion below
                with lock:
                    errors.append(exc)
            finally:
                close_old_connections()

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), len(set(results)), f"duplicate sequence numbers: {results}")
        self.assertEqual(len(results), 8)
