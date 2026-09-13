"""
Celery application wiring (no tasks yet).

Background jobs land here per domain as they're needed (master prompt §61:
reminders, scheduled invoices, notifications, document generation, external
sync, recurring jobs, limit alerts, overdue checks). Every task added later
must be idempotent — a retry must never create a duplicate invoice, payment,
or event (master prompt §62).
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("pausalac")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
