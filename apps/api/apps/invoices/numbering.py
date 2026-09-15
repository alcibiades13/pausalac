"""
Server-side invoice numbering (master prompt §95: never trust a
frontend-generated number; concurrent creation must not produce
duplicates). Assigned only at issue time — see apps/invoices/models.py.

Format `{PREFIX}-{year}-{seq:03d}` matches the master prompt's own
examples (§13, §21) for the plain invoice case, but has NOT been verified
against authoritative Serbian invoicing requirements (continuity rules,
whether an annual reset is even allowed, whether "INV" is the right
prefix for a Serbian-market document). The per-document-type prefixes
(PRO-/AVN-, Phase 6c) are this project's own invented convention on top
of that — Profaktura/Avans numbering isn't specified anywhere in either
spec document at all. Confirm before any of this is used for real
invoices — see docs/decisions-log.md.
"""

from django.db import transaction

from .models import Invoice, InvoiceSequence

PREFIXES = {
    Invoice.DocumentType.INVOICE: "INV",
    Invoice.DocumentType.PROFORMA: "PRO",
    Invoice.DocumentType.ADVANCE: "AVN",
}


def assign_invoice_number(invoice: Invoice) -> str:
    year = invoice.issue_date.year
    with transaction.atomic():
        sequence, _ = InvoiceSequence.objects.select_for_update().get_or_create(
            company=invoice.company, year=year, document_type=invoice.document_type
        )
        sequence.last_number += 1
        sequence.save(update_fields=["last_number"])
        prefix = PREFIXES[invoice.document_type]
        return f"{prefix}-{year}-{sequence.last_number:03d}"
