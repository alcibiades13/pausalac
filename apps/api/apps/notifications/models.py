"""
In-app + email notifications (master prompt §27/§99, blueprint §20).
One row per (recipient, channel) — a critical event that goes to both
in_app and email produces two rows, not one row with a channel list,
matching §27's own field list literally.
"""

from django.db import models

from apps.accounts.models import User
from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company


class Notification(models.Model):
    class Priority(models.TextChoices):
        CRITICAL = "critical", "Kritično"
        ATTENTION = "attention", "Pažnja"
        INFORMATIONAL = "informational", "Informativno"

    class Channel(models.TextChoices):
        IN_APP = "in_app", "U aplikaciji"
        EMAIL = "email", "Email"

    class Status(models.TextChoices):
        PENDING = "pending", "Na čekanju"
        SENT = "sent", "Poslato"
        FAILED = "failed", "Neuspešno"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")

    event_type = models.CharField(max_length=100)
    # Dedup backstop (§99) — the two current event sources only ever fire
    # once per row already (see apps/invoices|taxes/services.py), this is
    # defensive, not the primary mechanism.
    dedup_key = models.CharField(max_length=255)

    priority = models.CharField(max_length=20, choices=Priority.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Mirrors the Dashboard attention-item action shape (apps/analytics/views.py).
    action_route = models.CharField(max_length=100, blank=True)
    action_query = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "obaveštenje"
        verbose_name_plural = "obaveštenja"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipient", "channel", "dedup_key"],
                name="unique_notification_per_recipient_channel_dedup",
            )
        ]

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.recipient_id} ({self.channel})"
