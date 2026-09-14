"""
Manual/cron/testing entry point for the same sweep Celery Beat runs daily
(apps/subscriptions/tasks.py::send_trial_warnings_task).
"""

from django.core.management.base import BaseCommand

from apps.subscriptions.services import SubscriptionService


class Command(BaseCommand):
    help = "Notify companies whose trial ends within the next few days."

    def handle(self, *args, **options):
        count = SubscriptionService.send_trial_warnings()
        self.stdout.write(self.style.SUCCESS(f"Poslato upozorenja: {count}."))
