"""
Document library (master prompt §26, blueprint §6.8) — object-storage
backed, never a plain filesystem file. First real FileField in the
codebase; invoice/KPO PDFs are generated on-the-fly HTTP responses and
never persisted here (see docs/decisions-log.md).
"""

import uuid

from django.db import models

from apps.accounts.models import User
from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company
from apps.taxes.models import TaxResolution


def document_upload_path(instance: "Document", filename: str) -> str:
    return f"documents/{instance.company_id}/{uuid.uuid4().hex}_{filename}"


class Document(models.Model):
    class Category(models.TextChoices):
        TAX_RESOLUTION = "tax_resolution", "Poresko rešenje"
        CONTRACT = "contract", "Ugovor"
        SEF_DOCUMENT = "sef_document", "SEF dokument"
        FISCAL_RECEIPT = "fiscal_receipt", "Fiskalni račun"
        OTHER = "other", "Ostalo"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    category = models.CharField(max_length=20, choices=Category.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    file = models.FileField(upload_to=document_upload_path)
    # Snapshotted from the upload at creation time, not re-derived from
    # the storage backend later.
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()

    # Links an uploaded rešenje scan to the resolution record it
    # documents (apps.taxes.TaxResolution) — optional, the only "related
    # entity" concrete enough to model directly this phase.
    tax_resolution = models.ForeignKey(
        TaxResolution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "dokument"
        verbose_name_plural = "dokumenti"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
