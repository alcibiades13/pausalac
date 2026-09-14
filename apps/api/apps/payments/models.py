"""
Payment domain — depends on apps.invoices (a payment is always against an
invoice), same dependency direction as clients->invoices. A Payment is a
first-class object (master prompt §96), never just an
`invoice.is_paid = True` flag.
"""

from django.db import models

from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company
from apps.invoices.models import Invoice


class Payment(models.Model):
    class Method(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Uplata na račun"
        CASH = "cash", "Gotovina"
        OTHER = "other", "Ostalo"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    # Snapshotted from the invoice at record time, not joined live — same
    # §63 reasoning as FinancialEvent.currency.
    currency = models.CharField(max_length=3)
    paid_at = models.DateField("datum uplate")
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.BANK_TRANSFER)
    notes = models.TextField(blank=True)
    # Blank by default (e.g. payments entered via /admin); the frontend
    # always sends one so a retried "record payment" request can be
    # recognized and replayed instead of double-counted (master prompt
    # §62 — the literal "clicks Mark as paid twice" scenario).
    idempotency_key = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "uplata"
        verbose_name_plural = "uplate"
        ordering = ["-paid_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="unique_payment_idempotency_key_per_company",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0), name="payment_amount_positive"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.amount} {self.currency} / {self.invoice_id}"
