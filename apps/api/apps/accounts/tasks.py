"""
Email sending is always backgrounded (master prompt §60/§61) — views never
call `send_mail` directly. Templated via apps.notifications.email.EmailService
(Phase 6e) — lazy-imported since apps.notifications sits after apps.accounts
in DOMAIN_APPS.
"""

import logging

from celery import shared_task

from .models import User
from .services import email_verification_link, password_reset_link

logger = logging.getLogger("pausalac.accounts")


@shared_task
def send_verification_email_task(user_id: int) -> None:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_verification_email_task: user %s no longer exists", user_id)
        return

    from apps.notifications.email import EmailService

    EmailService.send(
        "verification",
        {"link": email_verification_link(user)},
        to=[user.email],
        subject="Potvrdi svoju email adresu — Pausalac",
    )


@shared_task
def send_password_reset_email_task(user_id: int) -> None:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_password_reset_email_task: user %s no longer exists", user_id)
        return

    from apps.notifications.email import EmailService

    EmailService.send(
        "password_reset",
        {"link": password_reset_link(user)},
        to=[user.email],
        subject="Resetovanje lozinke — Pausalac",
    )
