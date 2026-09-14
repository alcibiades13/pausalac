"""
Manual/cron/testing entry point for the same sweep Celery Beat runs daily
(apps/subscriptions/tasks.py::expire_trials_task).
"""

from django.core.management.base import BaseCommand

from apps.subscriptions.services import SubscriptionService


class Command(BaseCommand):
    help = "Flip TRIALING subscriptions past trial_ends_at to EXPIRED."

    def handle(self, *args, **options):
        count = SubscriptionService.expire_trials()
        self.stdout.write(self.style.SUCCESS(f"Isteklo probnih perioda: {count}."))
