"""
Accounting organization / connection business logic (master prompt §112:
views stay thin). The core trick this service implements: an accounting
org's access to a client company is a *real* `apps.companies.Membership`
row, auto-provisioned when a connection becomes active and kept in sync
as staff/connections change — so the entire existing RBAC/tenant-scoping
stack (HasCompanyPermission, X-Company-Id) needs zero changes to support
accountants. See docs/decisions-log.md for the fuller rationale.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.audit.services import AuditService
from apps.companies.models import Company, Membership

from .models import (
    AccountingConnection,
    AccountingOrganization,
    AccountingOrganizationMembership,
    SyncedMembership,
)


def _grant_membership(
    company: Company, user: User, role: str, connection: AccountingConnection
) -> None:
    """Provisions (or reactivates) a real Membership for `user` on
    `company` and records it as synced from `connection`. Skips a user who
    already has an *active*, independently-held Membership — this never
    overwrites someone's own role (e.g. the client's OWNER)."""
    membership, created = Membership.objects.get_or_create(
        user=user, company=company, defaults={"role": role, "status": Membership.Status.ACTIVE}
    )
    if not created:
        if membership.status == Membership.Status.ACTIVE:
            return
        membership.status = Membership.Status.ACTIVE
        membership.role = role
        membership.revoked_at = None
        membership.save(update_fields=["status", "role", "revoked_at"])

    SyncedMembership.objects.get_or_create(connection=connection, membership=membership)


class AccountingService:
    @staticmethod
    @transaction.atomic
    def create_organization(
        user: User, *, name: str, contact_email: str = "", pib: str | None = None
    ) -> AccountingOrganization:
        organization = AccountingOrganization.objects.create(
            name=name, contact_email=contact_email, pib=pib
        )
        AccountingOrganizationMembership.objects.create(
            user=user, organization=organization, role=AccountingOrganizationMembership.Role.ADMIN
        )
        return organization

    @staticmethod
    @transaction.atomic
    def add_staff(
        organization: AccountingOrganization, *, email: str, role: str, actor: User
    ) -> AccountingOrganizationMembership:
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise ValidationError(
                {"email": "Ne postoji korisnik sa ovom email adresom — mora prvo da se registruje."}
            ) from exc

        membership, created = AccountingOrganizationMembership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={"role": role, "status": AccountingOrganizationMembership.Status.ACTIVE},
        )
        if not created:
            if membership.status == AccountingOrganizationMembership.Status.ACTIVE:
                raise ValidationError({"email": "Korisnik je već član ove agencije."})
            membership.status = AccountingOrganizationMembership.Status.ACTIVE
            membership.role = role
            membership.save(update_fields=["status", "role"])

        active_connections = AccountingConnection.objects.filter(
            organization=organization, status=AccountingConnection.Status.ACTIVE
        )
        for connection in active_connections:
            _grant_membership(connection.company, user, connection.granted_role, connection)

        AuditService.log(
            actor=actor,
            entity_type="accounting_organization_membership",
            entity_id=membership.id,
            action="staff_added",
            new_value={"user": user.id, "role": role},
        )
        return membership

    @staticmethod
    @transaction.atomic
    def remove_staff(org_membership: AccountingOrganizationMembership, actor: User) -> None:
        org_membership.status = AccountingOrganizationMembership.Status.REVOKED
        org_membership.save(update_fields=["status"])

        synced = SyncedMembership.objects.filter(
            connection__organization=org_membership.organization,
            membership__user=org_membership.user,
        ).select_related("membership")
        for entry in synced:
            membership = entry.membership
            if membership.status != Membership.Status.REVOKED:
                membership.status = Membership.Status.REVOKED
                membership.revoked_at = timezone.now()
                membership.save(update_fields=["status", "revoked_at"])

        AuditService.log(
            actor=actor,
            entity_type="accounting_organization_membership",
            entity_id=org_membership.id,
            action="staff_removed",
            old_value={"status": "active"},
            new_value={"status": "revoked"},
        )

    @staticmethod
    @transaction.atomic
    def create_connection(
        organization: AccountingOrganization, *, company_pib: str, granted_role: str, actor: User
    ) -> AccountingConnection:
        company = Company.objects.filter(pib=company_pib).first()
        if company is None:
            raise ValidationError({"company_pib": "Kompanija sa ovim PIB-om nije pronađena."})

        exists = AccountingConnection.objects.filter(
            company=company,
            organization=organization,
            status__in=[AccountingConnection.Status.PENDING, AccountingConnection.Status.ACTIVE],
        ).exists()
        if exists:
            raise ValidationError("Veza sa ovom kompanijom već postoji ili je na čekanju.")

        connection = AccountingConnection.objects.create(
            company=company, organization=organization, granted_role=granted_role, invited_by=actor
        )
        AuditService.log(
            actor=actor,
            company=company,
            entity_type="accounting_connection",
            entity_id=connection.id,
            action="requested",
            new_value={"organization": organization.id, "granted_role": granted_role},
        )

        # Lazy import — apps.notifications sits after apps.accounting in
        # DOMAIN_APPS (config/settings/base.py); same precedent as
        # InvoiceService/TaxService's mark_overdue_all.
        from apps.notifications.models import Notification
        from apps.notifications.services import NotificationService

        NotificationService.notify_company(
            company,
            event_type="accounting_connection_requested",
            dedup_key=f"accounting_connection_requested:{connection.id}",
            priority=Notification.Priority.ATTENTION,
            title="Zahtev za povezivanje sa računovođom",
            message=f'"{organization.name}" želi da se poveže sa vašom kompanijom kao računovođa.',
            action_route="accounting",
            permission_codename="manage_users",
        )
        return connection

    @staticmethod
    @transaction.atomic
    def accept_connection(connection: AccountingConnection, actor: User) -> AccountingConnection:
        old_status = connection.status
        connection.status = AccountingConnection.Status.ACTIVE
        connection.accepted_at = timezone.now()
        connection.save(update_fields=["status", "accepted_at"])

        active_staff = AccountingOrganizationMembership.objects.filter(
            organization=connection.organization,
            status=AccountingOrganizationMembership.Status.ACTIVE,
        )
        for staff in active_staff:
            _grant_membership(connection.company, staff.user, connection.granted_role, connection)

        AuditService.log(
            actor=actor,
            company=connection.company,
            entity_type="accounting_connection",
            entity_id=connection.id,
            action="accepted",
            old_value={"status": old_status},
            new_value={"status": connection.status},
        )
        return connection

    @staticmethod
    def decline_connection(connection: AccountingConnection, actor: User) -> AccountingConnection:
        old_status = connection.status
        connection.status = AccountingConnection.Status.DECLINED
        connection.save(update_fields=["status"])
        AuditService.log(
            actor=actor,
            company=connection.company,
            entity_type="accounting_connection",
            entity_id=connection.id,
            action="declined",
            old_value={"status": old_status},
            new_value={"status": connection.status},
        )
        return connection

    @staticmethod
    @transaction.atomic
    def revoke_connection(connection: AccountingConnection, actor: User) -> AccountingConnection:
        old_status = connection.status
        connection.status = AccountingConnection.Status.REVOKED
        connection.revoked_at = timezone.now()
        connection.save(update_fields=["status", "revoked_at"])

        synced = connection.synced_memberships.select_related("membership")
        for entry in synced:
            membership = entry.membership
            if membership.status != Membership.Status.REVOKED:
                membership.status = Membership.Status.REVOKED
                membership.revoked_at = timezone.now()
                membership.save(update_fields=["status", "revoked_at"])

        AuditService.log(
            actor=actor,
            company=connection.company,
            entity_type="accounting_connection",
            entity_id=connection.id,
            action="revoked",
            old_value={"status": old_status},
            new_value={"status": connection.status},
        )
        return connection
