"""
Reusable email service (master prompt §107 EMAIL SYSTEM: "Create
reusable email service... Use background jobs"). Renders an HTML
template wrapped in the shared templates/emails/base.html layout and
sends a real multipart (plain-text + HTML) message — the mechanism every
domain's email-sending task calls through instead of hand-building
strings inline. Every current call site (verification, password reset,
invoice-sent) is refactored onto this in the same phase that introduces
it (Phase 6e).

Always called from inside a Celery task, never synchronously from a
view — the same discipline every email-sending task in this codebase
already documents on itself.
"""

from __future__ import annotations

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailService:
    @staticmethod
    def send(
        template_name: str,
        context: dict,
        *,
        to: list[str],
        subject: str,
        attachments: list[tuple[str, bytes, str]] | None = None,
    ) -> None:
        html_body = render_to_string(f"emails/{template_name}.html", context)
        text_body = strip_tags(html_body)
        email = EmailMultiAlternatives(subject=subject, body=text_body, to=to)
        email.attach_alternative(html_body, "text/html")
        for filename, content, mimetype in attachments or []:
            email.attach(filename, content, mimetype)
        email.send()
