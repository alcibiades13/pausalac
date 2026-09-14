from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.notifications.models import Notification

from ..models import AccountingOrganizationMembership
from ..services import AccountingService


class AccountingOrganizationViewSetTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@agencija.rs", password="s3cr3t-pass")
        self.staff = User.objects.create_user(email="staff@agencija.rs", password="s3cr3t-pass")
        self.org = AccountingService.create_organization(self.admin, name="Agencija A")

    def test_create_provisions_creator_as_admin(self):
        self.client.login(username="staff@agencija.rs", password="s3cr3t-pass")
        url = reverse("accounting-organization-list", kwargs={"version": "v1"})
        response = self.client.post(url, {"name": "Nova agencija"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["my_role"], "admin")

    def test_list_shows_only_my_organizations(self):
        self.client.login(username="staff@agencija.rs", password="s3cr3t-pass")
        url = reverse("accounting-organization-list", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.json()["results"], [])

    def test_admin_can_add_staff(self):
        self.client.login(username="admin@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-staff", kwargs={"version": "v1", "pk": self.org.id}
        )
        response = self.client.post(
            url, {"email": self.staff.email, "role": "staff"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            AccountingOrganizationMembership.objects.filter(
                organization=self.org, user=self.staff
            ).exists()
        )

    def test_non_admin_staff_cannot_add_staff(self):
        AccountingService.add_staff(
            self.org, email=self.staff.email, role="staff", actor=self.admin
        )
        another = User.objects.create_user(email="third@agencija.rs", password="s3cr3t-pass")
        self.client.login(username="staff@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-staff", kwargs={"version": "v1", "pk": self.org.id}
        )
        response = self.client.post(
            url, {"email": another.email, "role": "staff"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_can_list_staff(self):
        AccountingService.add_staff(
            self.org, email=self.staff.email, role="staff", actor=self.admin
        )
        self.client.login(username="staff@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-staff", kwargs={"version": "v1", "pk": self.org.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_outsider_cannot_retrieve_organization(self):
        # 404, not 403: get_queryset() already scopes to the caller's own
        # org memberships — same convention as CompanyViewSet (see
        # apps.companies.tests.test_views.test_cannot_retrieve_other_users_company).
        User.objects.create_user(email="outsider@x.rs", password="s3cr3t-pass")
        self.client.login(username="outsider@x.rs", password="s3cr3t-pass")
        url = reverse("accounting-organization-detail", kwargs={"version": "v1", "pk": self.org.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_admin_can_remove_staff(self):
        membership = AccountingService.add_staff(
            self.org, email=self.staff.email, role="staff", actor=self.admin
        )
        self.client.login(username="admin@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-remove-staff",
            kwargs={"version": "v1", "pk": self.org.id, "membership_id": membership.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            AccountingOrganizationMembership.objects.filter(
                id=membership.id, status=AccountingOrganizationMembership.Status.ACTIVE
            ).exists()
        )

    def test_non_admin_staff_cannot_remove_staff(self):
        membership = AccountingService.add_staff(
            self.org, email=self.staff.email, role="staff", actor=self.admin
        )
        another = User.objects.create_user(email="third@agencija.rs", password="s3cr3t-pass")
        AccountingService.add_staff(self.org, email=another.email, role="staff", actor=self.admin)
        self.client.login(username="staff@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-remove-staff",
            kwargs={"version": "v1", "pk": self.org.id, "membership_id": membership.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)


class AccountingConnectionFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@agencija.rs", password="s3cr3t-pass")
        self.owner = User.objects.create_user(email="owner@firma.rs", password="s3cr3t-pass")
        self.other_member = User.objects.create_user(
            email="member@firma.rs", password="s3cr3t-pass"
        )
        self.org = AccountingService.create_organization(self.admin, name="Agencija A")
        self.company = Company.objects.create(name="Firma A", pib="222222222")
        Membership.objects.create(user=self.owner, company=self.company)
        Membership.objects.create(
            user=self.other_member, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}

    def _create_connection_via_org(self):
        self.client.login(username="admin@agencija.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-connections", kwargs={"version": "v1", "pk": self.org.id}
        )
        response = self.client.post(
            url,
            {"company_pib": self.company.pib, "granted_role": "accountant"},
            content_type="application/json",
        )
        self.client.logout()
        return response

    def test_create_connection_notifies_owner(self):
        response = self._create_connection_via_org()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner, event_type="accounting_connection_requested"
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                recipient=self.other_member, event_type="accounting_connection_requested"
            ).exists()
        )

    def test_full_accept_flow_grants_access(self):
        response = self._create_connection_via_org()
        connection_id = response.json()["id"]

        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        list_url = reverse("accounting-connection-list", kwargs={"version": "v1"})
        listing = self.client.get(list_url, **self.headers)
        self.assertEqual(listing.json()["count"], 1)

        accept_url = reverse(
            "accounting-connection-accept", kwargs={"version": "v1", "pk": connection_id}
        )
        accept_response = self.client.post(accept_url, **self.headers)
        self.assertEqual(accept_response.status_code, 200)
        self.assertEqual(accept_response.json()["status"], "active")

        self.assertTrue(
            Membership.objects.filter(
                user=self.admin, company=self.company, status=Membership.Status.ACTIVE
            ).exists()
        )

    def test_non_owner_cannot_accept(self):
        response = self._create_connection_via_org()
        connection_id = response.json()["id"]

        self.client.login(username="member@firma.rs", password="s3cr3t-pass")
        accept_url = reverse(
            "accounting-connection-accept", kwargs={"version": "v1", "pk": connection_id}
        )
        accept_response = self.client.post(accept_url, **self.headers)
        self.assertEqual(accept_response.status_code, 403)

    def test_decline_leaves_no_access(self):
        response = self._create_connection_via_org()
        connection_id = response.json()["id"]

        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        decline_url = reverse(
            "accounting-connection-decline", kwargs={"version": "v1", "pk": connection_id}
        )
        decline_response = self.client.post(decline_url, **self.headers)
        self.assertEqual(decline_response.status_code, 200)
        self.assertFalse(
            Membership.objects.filter(user=self.admin, company=self.company).exists()
        )

    def test_revoke_removes_access(self):
        response = self._create_connection_via_org()
        connection_id = response.json()["id"]

        self.client.login(username="owner@firma.rs", password="s3cr3t-pass")
        accept_url = reverse(
            "accounting-connection-accept", kwargs={"version": "v1", "pk": connection_id}
        )
        self.client.post(accept_url, **self.headers)

        revoke_url = reverse(
            "accounting-connection-revoke", kwargs={"version": "v1", "pk": connection_id}
        )
        revoke_response = self.client.post(revoke_url, **self.headers)
        self.assertEqual(revoke_response.status_code, 200)

        membership = Membership.objects.get(user=self.admin, company=self.company)
        self.assertEqual(membership.status, Membership.Status.REVOKED)

        # And the admin's request against this company's tenant scope now
        # fails — a real HasCompanyPermission re-check, not just a status
        # flag on the connection.
        self.client.logout()
        self.client.login(username="admin@agencija.rs", password="s3cr3t-pass")
        obligations_url = reverse("kpo-list", kwargs={"version": "v1"})
        blocked = self.client.get(obligations_url, **self.headers)
        self.assertEqual(blocked.status_code, 403)

    def test_tenant_isolation_client_side(self):
        other_company = Company.objects.create(name="Firma B", pib="333333333")
        other_owner = User.objects.create_user(email="ownerb@firmab.rs", password="s3cr3t-pass")
        Membership.objects.create(user=other_owner, company=other_company)

        self._create_connection_via_org()

        self.client.login(username="ownerb@firmab.rs", password="s3cr3t-pass")
        list_url = reverse("accounting-connection-list", kwargs={"version": "v1"})
        response = self.client.get(list_url, HTTP_X_COMPANY_ID=str(other_company.id))
        self.assertEqual(response.json()["count"], 0)

    def test_org_cannot_see_another_orgs_connections(self):
        self._create_connection_via_org()
        other_admin = User.objects.create_user(
            email="other-admin@agencija-b.rs", password="s3cr3t-pass"
        )
        other_org = AccountingService.create_organization(other_admin, name="Agencija B")

        self.client.login(username="other-admin@agencija-b.rs", password="s3cr3t-pass")
        url = reverse(
            "accounting-organization-connections", kwargs={"version": "v1", "pk": other_org.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.json(), [])
