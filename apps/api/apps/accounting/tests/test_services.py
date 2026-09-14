from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.companies.models import Company, Membership

from ..models import AccountingConnection, AccountingOrganizationMembership, SyncedMembership
from ..services import AccountingService


class AccountingServiceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@agencija.rs", password="s3cr3t-pass")
        self.staff = User.objects.create_user(email="staff@agencija.rs", password="s3cr3t-pass")
        self.client_owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A", pib="111111111")
        Membership.objects.create(user=self.client_owner, company=self.company)

    def test_create_organization_provisions_creator_as_admin(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        membership = AccountingOrganizationMembership.objects.get(user=self.admin, organization=org)
        self.assertEqual(membership.role, AccountingOrganizationMembership.Role.ADMIN)
        self.assertEqual(membership.status, AccountingOrganizationMembership.Status.ACTIVE)

    def test_add_staff_syncs_onto_active_connections(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.accept_connection(connection, actor=self.client_owner)

        AccountingService.add_staff(org, email=self.staff.email, role="staff", actor=self.admin)

        membership = Membership.objects.get(user=self.staff, company=self.company)
        self.assertEqual(membership.role, "accountant")
        self.assertEqual(membership.status, Membership.Status.ACTIVE)
        self.assertTrue(
            SyncedMembership.objects.filter(connection=connection, membership=membership).exists()
        )

    def test_add_staff_skips_user_with_existing_active_membership(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.accept_connection(connection, actor=self.client_owner)

        # client_owner is independently the OWNER of self.company — adding
        # them as org staff must never downgrade their existing role.
        AccountingService.add_staff(
            org, email=self.client_owner.email, role="staff", actor=self.admin
        )

        membership = Membership.objects.get(user=self.client_owner, company=self.company)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertFalse(SyncedMembership.objects.filter(membership=membership).exists())

    def test_add_staff_rejects_duplicate(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        AccountingService.add_staff(org, email=self.staff.email, role="staff", actor=self.admin)
        with self.assertRaises(ValidationError):
            AccountingService.add_staff(org, email=self.staff.email, role="staff", actor=self.admin)

    def test_add_staff_rejects_unknown_email(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        with self.assertRaises(ValidationError):
            AccountingService.add_staff(
                org, email="nepostojeci@negde.rs", role="staff", actor=self.admin
            )

    def test_remove_staff_revokes_only_that_users_synced_memberships(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.accept_connection(connection, actor=self.client_owner)
        staff_membership = AccountingService.add_staff(
            org, email=self.staff.email, role="staff", actor=self.admin
        )

        AccountingService.remove_staff(staff_membership, actor=self.admin)

        removed = Membership.objects.get(user=self.staff, company=self.company)
        self.assertEqual(removed.status, Membership.Status.REVOKED)
        self.assertIsNotNone(removed.revoked_at)
        # The admin (still an active org member) keeps their own access.
        kept = Membership.objects.get(user=self.admin, company=self.company)
        self.assertEqual(kept.status, Membership.Status.ACTIVE)
        # The client's own OWNER membership is untouched.
        owner_membership = Membership.objects.get(user=self.client_owner, company=self.company)
        self.assertEqual(owner_membership.status, Membership.Status.ACTIVE)

    def test_create_connection_rejects_duplicate_pending_or_active(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        with self.assertRaises(ValidationError):
            AccountingService.create_connection(
                org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
            )

    def test_create_connection_allows_reinvite_after_decline(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        first = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.decline_connection(first, actor=self.client_owner)

        second = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(
            AccountingConnection.objects.filter(company=self.company, organization=org).count(), 2
        )

    def test_create_connection_unknown_pib_raises(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        with self.assertRaises(ValidationError):
            AccountingService.create_connection(
                org, company_pib="000000000", granted_role="accountant", actor=self.admin
            )

    def test_accept_connection_syncs_active_staff_with_granted_role(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        AccountingService.add_staff(org, email=self.staff.email, role="staff", actor=self.admin)
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant_admin", actor=self.admin
        )

        AccountingService.accept_connection(connection, actor=self.client_owner)

        for user in (self.admin, self.staff):
            membership = Membership.objects.get(user=user, company=self.company)
            self.assertEqual(membership.role, "accountant_admin")

    def test_decline_connection_creates_no_memberships(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.decline_connection(connection, actor=self.client_owner)
        self.assertFalse(Membership.objects.filter(user=self.admin, company=self.company).exists())

    def test_revoke_connection_revokes_exactly_synced_memberships(self):
        org = AccountingService.create_organization(self.admin, name="Agencija A")
        AccountingService.add_staff(org, email=self.staff.email, role="staff", actor=self.admin)
        connection = AccountingService.create_connection(
            org, company_pib=self.company.pib, granted_role="accountant", actor=self.admin
        )
        AccountingService.accept_connection(connection, actor=self.client_owner)

        AccountingService.revoke_connection(connection, actor=self.client_owner)

        for user in (self.admin, self.staff):
            membership = Membership.objects.get(user=user, company=self.company)
            self.assertEqual(membership.status, Membership.Status.REVOKED)
        owner_membership = Membership.objects.get(user=self.client_owner, company=self.company)
        self.assertEqual(owner_membership.status, Membership.Status.ACTIVE)
