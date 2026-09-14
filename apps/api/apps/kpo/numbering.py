"""
Server-side KPO row numbering — mirrors apps.invoices.numbering exactly
(same concurrency-safety reasoning, master prompt §95).

Resets per calendar year, same UNVERIFIED assumption already flagged for
invoice numbering — see docs/decisions-log.md. Confirm before this is
relied on for a real filing.
"""

from datetime import date

from django.db import transaction

from .models import KPOSequence


def assign_sequence_number(entry_date: date, company) -> int:
    year = entry_date.year
    with transaction.atomic():
        sequence, _ = KPOSequence.objects.select_for_update().get_or_create(
            company=company, year=year
        )
        sequence.last_number += 1
        sequence.save(update_fields=["last_number"])
        return sequence.last_number
