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
