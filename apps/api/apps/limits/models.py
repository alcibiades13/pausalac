"""
Versioned regulatory rules (master prompt §25, blueprint §16) — the
single place a regulatory number (a limit, a threshold, a cap) lives,
instead of being hardcoded in business logic wherever it's used.
"""

from django.db import models


class RegulatoryRule(models.Model):
    """
    Platform-wide, not tenant-scoped — the same rule applies to every
    company. `config` shape depends on `identifier` (e.g. an amount +
    currency + period for a turnover limit, a bare percentage for a
    growth cap) — see apps.limits.rules.get_active_rule for how a rule
    is looked up for a given date.
    """

    class ApprovalStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Nepotvrđeno"
        CONFIRMED = "confirmed", "Potvrđeno"

    identifier = models.CharField(max_length=100)
    config = models.JSONField()
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=255)
    version = models.PositiveIntegerField(default=1)
    approval_status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.UNVERIFIED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "regulatorno pravilo"
        verbose_name_plural = "regulatorna pravila"
        ordering = ["identifier", "-effective_from", "-version"]

    def __str__(self) -> str:
        return f"{self.identifier} v{self.version} ({self.effective_from})"
