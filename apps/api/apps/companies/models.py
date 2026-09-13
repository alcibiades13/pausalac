"""
Tenant model. `Company` is the tenant root every business-domain model
(clients, invoices, ...) will FK to in later phases. `Membership` is the
User <-> Company link that RBAC (apps.accounts.permissions) reads roles
from.
"""

from django.conf import settings
from django.db import models

from .managers import TenantScopedManager


class Company(models.Model):
    """
    Tenant root. `bank_account`/`uses_sef` were added in Phase 2a for
    onboarding-completion tracking (apps/companies/views.py::onboarding) —
    `uses_sef` is a user-declared preference only, not a real SEF
    integration (master prompt §39: architecture seam, not a fake one).
    """

    name = models.CharField("naziv", max_length=255)
    legal_name = models.CharField("pun naziv", max_length=255, blank=True)
    pib = models.CharField("PIB", max_length=20, unique=True, null=True, blank=True)
    address = models.CharField("adresa", max_length=255, blank=True)
    city = models.CharField("grad", max_length=120, blank=True)
    country = models.CharField("država", max_length=2, default="RS")
    activity_code = models.CharField("šifra delatnosti", max_length=20, blank=True)
    default_currency = models.CharField("podrazumevana valuta", max_length=3, default="RSD")
    # Deliberately unvalidated format (IBAN/domestic account, either) — no
    # confirmed authoritative format rule to encode yet (master prompt §81).
    bank_account = models.CharField("račun za uplate", max_length=64, blank=True)
    uses_sef = models.BooleanField("koristi SEF", default=False)
    is_active = models.BooleanField("aktivna", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "kompanija"
        verbose_name_plural = "kompanije"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    """User <-> Company link carrying the company-scoped RBAC role."""

    class Role(models.TextChoices):
        OWNER = "owner", "Vlasnik"
        # Unused until Phase 4's accounting platform, but present now so
        # that phase doesn't need a migration reshuffle (master prompt §30).
        ACCOUNTANT = "accountant", "Računovođa"
        ACCOUNTANT_ADMIN = "accountant_admin", "Računovođa (admin)"

    class Status(models.TextChoices):
        ACTIVE = "active", "Aktivan"
        INVITED = "invited", "Pozvan"
        REVOKED = "revoked", "Opozvan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OWNER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    # First real usage of the tenant-scoping manager (apps.companies.managers)
    # that later domain models (Client, Invoice, ...) will adopt as their
    # *default* manager — kept secondary here since Membership rows aren't
    # themselves tenant-owned data in the same sense.
    by_company = TenantScopedManager()

    class Meta:
        verbose_name = "članstvo"
        verbose_name_plural = "članstva"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"], name="unique_membership_per_user_company"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.company_id} ({self.role})"
