"""
Invoice domain: model, server-side numbering, and the financial-event
ledger (master prompt §21). Status transitions and numbering assignment
live in services.py/numbering.py, not here — models stay declarative.
"""

from decimal import Decimal

from django.db import models

from apps.clients.models import Client
from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Nacrt"
        ISSUED = "issued", "Izdata"
        # Reachable starting Phase 2c/2d (email sending, view tracking,
        # payments) — defined now so this enum/constraint never needs a
        # migration again, only the transition map in services.py grows.
        SENT = "sent", "Poslata"
        VIEWED = "viewed", "Viđena"
        PARTIALLY_PAID = "partially_paid", "Delimično plaćena"
        PAID = "paid", "Plaćena"
        OVERDUE = "overdue", "Kasni"
        CANCELLED = "cancelled", "Stornirana"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoices")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="invoices")

    # Null while DRAFT — assigned by apps.invoices.numbering only at issue
    # time, so abandoned drafts don't burn sequence numbers. Format/rule
    # NOT verified against authoritative Serbian invoicing requirements —
    # see docs/decisions-log.md.
    invoice_number = models.CharField(max_length=32, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    issue_date = models.DateField("datum izdavanja")
    due_date = models.DateField("rok plaćanja")
    service_date = models.DateField("datum prometa")

    # Minimum field per master prompt §11. No currency picker or exchange
    # rate logic yet (§37/§38 are V2/NBS integration) — set from
    # company.default_currency at creation, effectively RSD-only for now.
    currency = models.CharField(max_length=3, default="RSD")

    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)

    issued_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "faktura"
        verbose_name_plural = "fakture"
        ordering = ["-issue_date", "-id"]
        constraints = [
            # Plain unique constraint — standard SQL NULL semantics already
            # let multiple DRAFT invoices (invoice_number=NULL) coexist
            # without a partial-index trick.
            models.UniqueConstraint(
                fields=["company", "invoice_number"], name="unique_invoice_number_per_company"
            ),
            # Hardcoded rather than Status.values: a nested Meta class body
            # can't see names from its enclosing class body (Status is
            # defined on Invoice, one level up) — and Django serializes
            # CheckConstraints into migrations as literal values either
            # way, so this isn't losing any real DRY-ness. Keep in sync
            # with the Status choices above if a status is ever added.
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "draft",
                        "issued",
                        "sent",
                        "viewed",
                        "partially_paid",
                        "paid",
                        "overdue",
                        "cancelled",
                    ]
                ),
                name="invoice_status_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.invoice_number or f"(nacrt #{self.pk})"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "stavka fakture"
        verbose_name_plural = "stavke fakture"
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.description


class InvoiceSequence(models.Model):
    """
    One counter row per (company, year) — never exposed via the API.
    apps.invoices.numbering.assign_invoice_number is the only writer,
    always inside `select_for_update()` to stay race-safe under
    concurrent invoice issuance (master prompt §95).
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoice_sequences")
    year = models.PositiveIntegerField()
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "sekvenca brojeva faktura"
        verbose_name_plural = "sekvence brojeva faktura"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "year"], name="unique_sequence_per_company_year"
            )
        ]

    def __str__(self) -> str:
        return f"{self.company_id} / {self.year} -> {self.last_number}"


class FinancialEvent(models.Model):
    """
    Central ledger (master prompt §21) — the single source of truth later
    domains (KPO, Limits — Phase 3) read from instead of each computing
    revenue their own way. Append-only; nothing updates or deletes these.
    """

    class EventType(models.TextChoices):
        INVOICE_CREATED = "invoice_created", "Faktura kreirana"
        INVOICE_ISSUED = "invoice_issued", "Faktura izdata"
        INVOICE_SENT = "invoice_sent", "Faktura poslata"
        INVOICE_CANCELLED = "invoice_cancelled", "Faktura stornirana"
        INVOICE_PAID = "invoice_paid", "Faktura plaćena"
        INVOICE_PARTIALLY_PAID = "invoice_partially_paid", "Faktura delimično plaćena"
        FISCAL_RECEIPT_CREATED = "fiscal_receipt_created", "Fiskalni račun kreiran"
        FISCAL_RECEIPT_CANCELLED = "fiscal_receipt_cancelled", "Fiskalni račun storniran"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="financial_events")
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="financial_events", null=True, blank=True
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    # Snapshotted, not derived from a live join — master prompt §63:
    # historical financial records must not silently change if the
    # invoice/company they came from changes later.
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    occurred_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "finansijski događaj"
        verbose_name_plural = "finansijski događaji"
        ordering = ["-occurred_at"]
        indexes = [models.Index(fields=["company", "event_type", "-occurred_at"])]

    def __str__(self) -> str:
        return f"{self.event_type} / {self.amount} {self.currency}"
