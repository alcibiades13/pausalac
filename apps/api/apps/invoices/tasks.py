"""
Email sending is always backgrounded (master prompt §60/§61), same
pattern as apps/accounts/tasks.py. The ISSUED->SENT transition only
happens here, after the send actually succeeds — never eagerly in the
view — so the status can't claim "sent" for something delivery failed on.
"""

import logging

from celery import shared_task
from django.core.mail import EmailMessage

from apps.accounts.models import User

from .models import Invoice
from .pdf import render_invoice_pdf
from .services import InvoiceService

logger = logging.getLogger("pausalac.invoices")


@shared_task
def send_invoice_email_task(
    invoice_id: int, recipient_email: str, message: str, actor_id: int
) -> None:
    try:
        invoice = Invoice.objects.select_related("company", "client").get(pk=invoice_id)
    except Invoice.DoesNotExist:
        logger.warning("send_invoice_email_task: invoice %s no longer exists", invoice_id)
        return

    pdf_bytes = render_invoice_pdf(invoice)

    body = (
        f"Zdravo,\n\nU prilogu je faktura {invoice.invoice_number} od {invoice.company.name}, "
        f"za ukupan iznos {invoice.total} {invoice.currency}.\n"
    )
    if message:
        body += f"\n{message}\n"
    body += "\nHvala,\n" + invoice.company.name

    email = EmailMessage(
        subject=f"Faktura {invoice.invoice_number} — {invoice.company.name}",
        body=body,
        to=[recipient_email],
    )
    email.attach(f"{invoice.invoice_number}.pdf", pdf_bytes, "application/pdf")
    email.send()

    try:
        actor = User.objects.get(pk=actor_id)
    except User.DoesNotExist:
        actor = None
    InvoiceService.mark_sent(invoice, actor=actor)


@shared_task
def mark_overdue_invoices_task() -> int:
    """Celery Beat schedule: config/celery.py. Same function the
    `check_overdue_invoices` management command calls for manual/testing
    use — logic lives once in InvoiceService.mark_overdue_all."""
    return InvoiceService.mark_overdue_all()
