"""
KPO — Poslovna knjiga o ostvarenom prometu paušalno oporezovanih obveznika
(master prompt §20). Entries are generated automatically from Invoice
issuance/cancellation (apps.kpo.services.KPOService), never entered by
hand — see docs/decisions-log.md for the exact obrazac column mapping
this was built against.
"""

from decimal import Decimal

from django.db import models

from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company
from apps.invoices.models import Invoice


class KPOEntry(models.Model):
    class EntryType(models.TextChoices):
        ORIGINAL = "original", "Original"
        STORNO = "storno", "Storno"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="kpo_entries")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="kpo_entries")

    # "Redni broj poslovne promene" — assigned by apps.kpo.numbering,
    # never reused even after a storno (append-only, master prompt §63).
    sequence_number = models.PositiveIntegerField()

    # "Datum ... knjiženja" — the promet date (invoice.service_date), NOT
    # issue_date or a wall-clock timestamp. See docs/decisions-log.md for
    # the flagged inconsistency with how Phase 3a's Limits currently
    # compute revenue (occurred_at, not service_date) — not fixed here.
    entry_date = models.DateField()
    description = models.CharField(max_length=255)

    # Kolona 3 / kolona 4. Kolona 5 (svega prihodi) is product+service,
    # computed at read time rather than stored.
    product_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    service_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    entry_type = models.CharField(
        max_length=10, choices=EntryType.choices, default=EntryType.ORIGINAL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "KPO stavka"
        verbose_name_plural = "KPO stavke"
        ordering = ["sequence_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sequence_number"], name="unique_kpo_sequence_per_company"
            )
        ]

    @property
    def total_revenue(self) -> Decimal:
        return self.product_revenue + self.service_revenue

    def __str__(self) -> str:
        return f"KPO #{self.sequence_number} / {self.company_id}"


class KPOSequence(models.Model):
    """One counter row per (company, year) — mirrors InvoiceSequence
    exactly (apps/invoices/models.py). Never exposed via the API; written
    only by apps.kpo.numbering.assign_sequence_number under
    select_for_update()."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="kpo_sequences")
    year = models.PositiveIntegerField()
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "sekvenca KPO brojeva"
        verbose_name_plural = "sekvence KPO brojeva"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "year"], name="unique_kpo_sequence_per_company_year"
            )
        ]

    def __str__(self) -> str:
        return f"{self.company_id} / {self.year} -> {self.last_number}"
