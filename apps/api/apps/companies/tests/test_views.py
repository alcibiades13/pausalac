from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company, Membership


class CompanyCreationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        self.client.login(username="marko@pausalac.rs", password="s3cr3t-pass")

    def test_create_company_provisions_requesting_user_as_owner(self):
        url = reverse("company-list", kwargs={"version": "v1"})
        response = self.client.post(url, {"name": "Marko Marković PR"})
        self.assertEqual(response.status_code, 201)

        company = Company.objects.get(name="Marko Marković PR")
        membership = Membership.objects.get(user=self.user, company=company)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertEqual(membership.status, Membership.Status.ACTIVE)

    def test_create_company_requires_authentication(self):
        # 403, not 401: SessionAuthentication has no WWW-Authenticate
        # challenge to issue for anonymous requests — expected DRF behavior.
        self.client.logout()
        url = reverse("company-list", kwargs={"version": "v1"})
        response = self.client.post(url, {"name": "Anonimna Firma"})
        self.assertEqual(response.status_code, 403)


class CompanyTenantIsolationTests(TestCase):
    """Master prompt §47: cross-tenant access must be explicitly tested."""

    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)

    def test_list_only_shows_own_companies(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        response = self.client.get(reverse("company-list", kwargs={"version": "v1"}))
        names = [c["name"] for c in response.json()["results"]]
        self.assertEqual(names, ["Firma A"])

    def test_cannot_retrieve_other_users_company(self):
        # 404, not 403: get_queryset() already scopes to the caller's own
        # memberships, so another tenant's company isn't just forbidden —
        # it doesn't exist as far as this user's queryset is concerned
        # (avoids confirming the row exists at all).
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("company-detail", kwargs={"version": "v1", "pk": self.company_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_non_owner_cannot_patch_company(self):
        # An accountant-role membership (Phase 4 will create these via an
        # invite flow; inserted directly here since that flow doesn't exist
        # yet) must not be able to edit the company profile.
        Membership.objects.create(
            user=self.owner_b, company=self.company_a, role=Membership.Role.ACCOUNTANT
        )
        self.client.login(username="b@pausalac.rs", password="s3cr3t-pass")
        url = reverse("company-detail", kwargs={"version": "v1", "pk": self.company_a.pk})
        response = self.client.patch(url, {"name": "Hacked"}, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_members_endpoint_requires_manage_users_permission(self):
        Membership.objects.create(
            user=self.owner_b, company=self.company_a, role=Membership.Role.ACCOUNTANT
        )
        self.client.login(username="b@pausalac.rs", password="s3cr3t-pass")
        url = reverse("company-members", kwargs={"version": "v1", "pk": self.company_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_owner_can_list_members(self):
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        url = reverse("company-members", kwargs={"version": "v1", "pk": self.company_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
