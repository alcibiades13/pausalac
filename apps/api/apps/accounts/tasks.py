"""
Email sending is always backgrounded (master prompt §60/§61) — views never
call `send_mail` directly.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail

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

    link = email_verification_link(user)
    send_mail(
        subject="Potvrdi svoju email adresu — Pausalac",
        message=(
            f"Zdravo,\n\nPotvrdi svoju email adresu klikom na link ispod:\n\n{link}\n\n"
            "Ako nisi ti napravio nalog, slobodno ignoriši ovaj email."
        ),
        from_email=None,
        recipient_list=[user.email],
    )


@shared_task
def send_password_reset_email_task(user_id: int) -> None:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_password_reset_email_task: user %s no longer exists", user_id)
        return

    link = password_reset_link(user)
    send_mail(
        subject="Resetovanje lozinke — Pausalac",
        message=(
            f"Zdravo,\n\nNeko (nadamo se ti) je zatražio resetovanje lozinke. "
            f"Klikni na link ispod da postaviš novu lozinku:\n\n{link}\n\n"
            "Ako nisi ti zatražio ovo, slobodno ignoriši ovaj email — tvoja lozinka ostaje ista."
        ),
        from_email=None,
        recipient_list=[user.email],
    )
