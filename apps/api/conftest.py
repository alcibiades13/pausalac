"""
Project-wide pytest fixtures.

Phase 6a added cache-backed rate limiting (config/settings/base.py) —
Django's cache (LocMemCache in tests, config/settings/test.py) is
process-local but NOT reset between individual tests by Django's own
TestCase. Without this, throttle counters (and any other future
cache-backed state) silently accumulate across the whole pytest session,
so a test late in the run can fail from an earlier, unrelated test's
requests against the same endpoint — exactly the kind of test-order-
dependent flakiness this project's testing discipline has caught and
fixed before (see docs/decisions-log.md's TransactionTestCase/
serialized_rollback entry, a different mechanism for the same class of
problem: state silently surviving between tests that should be isolated).
"""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
