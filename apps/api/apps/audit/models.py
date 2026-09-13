"""
Append-only audit trail (master prompt §22). No update/delete is exposed
anywhere in the API or admin — see admin.py and views.py in this app.
"""

from django.conf import settings
from django.db import models


class AuditLogEntry(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
        help_text="Null for system/Celery-initiated actions.",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
        help_text="Null for actions with no single owning company (e.g. platform-level).",
    )
    entity_type = models.CharField(max_length=100)
    # Not a hard FK on purpose: audit history must survive the entity being
    # deleted/cancelled (master prompt §63 — never silently lose history).
    entity_id = models.CharField(max_length=64)
    action = models.CharField(max_length=100)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    source = models.CharField(
        max_length=20,
        choices=[
            ("api", "api"),
            ("admin", "admin"),
            ("system", "system"),
            ("celery", "celery"),
        ],
        default="api",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "audit zapis"
        verbose_name_plural = "audit zapisi"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["company", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} on {self.entity_type}:{self.entity_id}"
