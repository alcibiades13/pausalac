"""
Accounting organizations and their client connections (master prompt
§28-§31, Phase 4a). An accounting firm's staff need real access to a
client `Company` to do their job — that access is granted through actual
`apps.companies.Membership` rows (see AccountingService), not a parallel
permission system, so the entire existing RBAC/tenant-scoping stack needs
no changes at all. `SyncedMembership` is the bookkeeping that lets a
revoked connection remove exactly the memberships it created.
"""

from django.conf import settings
from django.db import models

from apps.companies.managers import TenantScopedManager
from apps.companies.models import Company, Membership


class AccountingOrganization(models.Model):
    """An accounting firm. Distinct from `Company` — an organization has no
    paušal/KPO/limits data of its own, only staff and client connections."""

    name = models.CharField("naziv", max_length=255)
    contact_email = models.EmailField("kontakt email", blank=True)
    pib = models.CharField("PIB", max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "računovodstvena agencija"
        verbose_name_plural = "računovodstvene agencije"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AccountingOrganizationMembership(models.Model):
    """User <-> AccountingOrganization link. A separate, org-scoped
    permission axis (admin/staff) from `Membership.Role` — two roles don't
    need a whole "permissions as data" dict of their own."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        STAFF = "staff", "Zaposleni"

    class Status(models.TextChoices):
        ACTIVE = "active", "Aktivan"
        REVOKED = "revoked", "Opozvan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounting_memberships"
    )
    organization = models.ForeignKey(
        AccountingOrganization, on_delete=models.CASCADE, related_name="staff_memberships"
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "članstvo u agenciji"
        verbose_name_plural = "članstva u agenciji"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"], name="unique_org_membership_per_user_org"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.organization_id} ({self.role})"


class AccountingConnection(models.Model):
    """Company <-> AccountingOrganization connection (master prompt §31).
    Append-only history, like `KPOEntry`/`FinancialEvent` — a declined or
    revoked connection is never deleted, only re-created for a fresh
    invite. The service layer enforces "at most one pending/active row per
    (company, organization) pair" rather than a DB constraint, so history
    can be preserved."""

    class Status(models.TextChoices):
        PENDING = "pending", "Na čekanju"
        ACTIVE = "active", "Aktivna"
        DECLINED = "declined", "Odbijena"
        REVOKED = "revoked", "Opozvana"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="accounting_connections"
    )
    organization = models.ForeignKey(
        AccountingOrganization, on_delete=models.CASCADE, related_name="connections"
    )
    granted_role = models.CharField(
        max_length=20,
        choices=[
            (Membership.Role.ACCOUNTANT, Membership.Role.ACCOUNTANT.label),
            (Membership.Role.ACCOUNTANT_ADMIN, Membership.Role.ACCOUNTANT_ADMIN.label),
        ],
        default=Membership.Role.ACCOUNTANT,
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    objects = TenantScopedManager()

    class Meta:
        verbose_name = "veza sa agencijom"
        verbose_name_plural = "veze sa agencijama"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.organization_id} -> {self.company_id} ({self.status})"


class SyncedMembership(models.Model):
    """Bookkeeping only, never exposed via the API: which `Membership` row
    was auto-provisioned by which `AccountingConnection`, so revoking a
    connection (or removing one staff member) touches only what it
    created."""

    connection = models.ForeignKey(
        AccountingConnection, on_delete=models.CASCADE, related_name="synced_memberships"
    )
    membership = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="synced_from"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "membership"], name="unique_synced_membership"
            )
        ]

    def __str__(self) -> str:
        return f"{self.connection_id} -> membership {self.membership_id}"
