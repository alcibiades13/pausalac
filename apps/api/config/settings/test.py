"""Settings used by the test suite (pytest.ini points here)."""

from .dev import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

# Run Celery tasks synchronously in tests — no Redis/worker needed, and
# `.delay()` calls (verification/reset emails) execute inline so their
# side effects (mail.outbox) are assertable.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Documents (Phase 3e) is the first real FileField in the codebase — base
# settings point at real S3/MinIO, which tests must never depend on.
# In-memory storage keeps file-upload tests fast and isolated.
STORAGES = {**STORAGES, "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"}}

# Phase 6a's rate limiting (config/settings/base.py) is cache-backed —
# base settings point at real Redis, which throttle *counters* must never
# accumulate against between test runs (dozens of test files call
# register/login in setUp(), which would eventually exceed the "auth"
# scope's 10/min against a real, persistent counter and produce flaky
# 429s). LocMemCache is process-local and starts fresh every run.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
