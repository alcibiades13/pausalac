"""
Email delivery for notifications — mirrors
apps.invoices.tasks.send_invoice_email_task's shape exactly (plain
EmailMessage, no template, DEFAULT_FROM_EMAIL implicit).
"""

import logging

from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import Notification

logger = logging.getLogger("pausalac.notifications")


@shared_task
def send_notification_email_task(notification_id: int) -> None:
    try:
        notification = Notification.objects.select_related("recipient").get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.warning(
            "send_notification_email_task: notification %s no longer exists", notification_id
        )
        return

    try:
        email = EmailMessage(
            subject=notification.title,
            body=notification.message,
            to=[notification.recipient.email],
        )
        email.send()
    except Exception:
        logger.exception(
            "send_notification_email_task: failed to send notification %s", notification_id
        )
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status"])
        return

    notification.status = Notification.Status.SENT
    notification.sent_at = timezone.now()
    notification.save(update_fields=["status", "sent_at"])
