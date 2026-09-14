"""
Celery application wiring, including the Beat schedule (master prompt §61:
reminders, scheduled invoices, notifications, document generation, external
sync, recurring jobs, limit alerts, overdue checks). Every task added later
must be idempotent — a retry must never create a duplicate invoice, payment,
or event (master prompt §62).

Beat runs embedded in the worker process for now (`celery -A config worker
-B`, see package.json's `dev` script) — the simplest option for a single-
worker dev/MVP setup; splitting it into its own process is a deploy-time
scaling concern, not a now concern.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("pausalac")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "mark-overdue-invoices": {
        "task": "apps.invoices.tasks.mark_overdue_invoices_task",
        "schedule": crontab(minute=0),  # hourly
    },
}
