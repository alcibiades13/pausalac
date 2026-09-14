from celery import shared_task

from .services import SubscriptionService


@shared_task
def expire_trials_task() -> int:
    """Beat schedule: config/celery.py."""
    return SubscriptionService.expire_trials()


@shared_task
def send_trial_warnings_task() -> int:
    """Beat schedule: config/celery.py."""
    return SubscriptionService.send_trial_warnings()
