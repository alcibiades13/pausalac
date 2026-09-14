"""
Manual/cron/testing entry point for the same overdue sweep Celery Beat
runs hourly (apps/taxes/tasks.py::mark_overdue_tax_obligations_task).
"""

from django.core.management.base import BaseCommand

from apps.taxes.services import TaxService


class Command(BaseCommand):
    help = "Flip PENDING tax obligations past their due date to OVERDUE."

    def handle(self, *args, **options):
        count = TaxService.mark_overdue_all()
        self.stdout.write(self.style.SUCCESS(f"Označeno kao 'kasni': {count} obaveza(a)."))
