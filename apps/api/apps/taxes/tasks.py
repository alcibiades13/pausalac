from celery import shared_task

from .services import TaxService


@shared_task
def mark_overdue_tax_obligations_task() -> int:
    """Celery Beat schedule: config/celery.py. Same function the
    check_overdue_tax_obligations management command calls for manual/
    testing use — logic lives once in TaxService.mark_overdue_all."""
    return TaxService.mark_overdue_all()
