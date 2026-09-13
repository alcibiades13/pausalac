"""Settings used by the test suite (pytest.ini points here)."""

from .dev import *  # Django multi-settings pattern (see pyproject.toml per-file-ignores)

# Run Celery tasks synchronously in tests — no Redis/worker needed, and
# `.delay()` calls (verification/reset emails) execute inline so their
# side effects (mail.outbox) are assertable.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
