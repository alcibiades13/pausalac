"""
Tax/contribution obligations (master prompt §23, blueprint §6.7) —
resolution-driven, not rate-computed. See docs/decisions-log.md for why:
the actual amount owed comes from each paušalac's individual poresko
rešenje, not from applying the reference rates to an assumed base.
"""

from decimal import Decimal

from django.db import models

from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company


class TaxResolution(models.Model):
    """
    A user-entered poresko rešenje. Immutable once created — no edit/
    delete endpoint this phase (see docs/decisions-log.md); generates
    one TaxObligation per calendar month in [effective_from, effective_until].
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="tax_resolutions")
    effective_from = models.DateField()
    effective_until = models.DateField()
    tax_base = models.DecimalField(max_digits=14, decimal_places=2)
    income_tax_amount = models.DecimalField(max_digits=14, decimal_places=2)
    pio_amount = models.DecimalField(max_digits=14, decimal_places=2)
    health_amount = models.DecimalField(max_digits=14, decimal_places=2)
    unemployment_amount = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "poresko rešenje"
        verbose_name_plural = "poreska rešenja"
        ordering = ["-effective_from"]

    def __str__(self) -> str:
        return f"Rešenje {self.company_id} ({self.effective_from} – {self.effective_until})"


class TaxObligation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Na čekanju"
        PAID = "paid", "Plaćeno"
        OVERDUE = "overdue", "Kasni"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="tax_obligations")
    resolution = models.ForeignKey(
        TaxResolution, on_delete=models.CASCADE, related_name="obligations"
    )

    # First day of the reporting month.
    period_start = models.DateField()
    due_date = models.DateField()

    # Snapshotted from the resolution at generation time — not a live
    # join, same reasoning as FinancialEvent/KPOEntry (master prompt §63).
    income_tax_amount = models.DecimalField(max_digits=14, decimal_places=2)
    pio_amount = models.DecimalField(max_digits=14, decimal_places=2)
    health_amount = models.DecimalField(max_digits=14, decimal_places=2)
    unemployment_amount = models.DecimalField(max_digits=14, decimal_places=2)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "poreska obaveza"
        verbose_name_plural = "poreske obaveze"
        ordering = ["period_start"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "period_start"], name="unique_tax_obligation_period_per_company"
            )
        ]

    @property
    def total_amount(self) -> Decimal:
        return (
            self.income_tax_amount + self.pio_amount + self.health_amount + self.unemployment_amount
        )

    def __str__(self) -> str:
        return f"{self.company_id} / {self.period_start} ({self.status})"
