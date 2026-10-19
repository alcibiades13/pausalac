"""
Manual/cron/testing entry point for the same overdue sweep Celery Beat
runs hourly (apps/invoices/tasks.py::mark_overdue_invoices_task). Useful
for verifying the feature without waiting for the schedule, and as a
fallback if Beat isn't running in a given environment.
"""

from django.core.management.base import BaseCommand

from apps.invoices.services import InvoiceService
from config.pluralize import pluralize_sr


class Command(BaseCommand):
    help = "Flip ISSUED/SENT/PARTIALLY_PAID invoices past their due date to OVERDUE."

    def handle(self, *args, **options):
        count = InvoiceService.mark_overdue_all()
        noun = pluralize_sr(count, "faktura", "fakture", "faktura")
        self.stdout.write(self.style.SUCCESS(f"Označeno kao 'kasni': {count} {noun}."))
