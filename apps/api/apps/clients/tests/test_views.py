from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.companies.models import Company, Membership


class ClientCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.list_url = reverse("client-list", kwargs={"version": "v1"})

    def _headers(self, company=None):
        return {"HTTP_X_COMPANY_ID": str((company or self.company).id)}

    def test_create_client(self):
        response = self.client.post(
            self.list_url,
            {"name": "Marko Marković", "client_type": "individual", "email": "marko@primer.rs"},
            **self._headers(),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Client.objects.for_company(self.company).count(), 1)

    def test_list_requires_company_header(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 400)

    def test_update_client(self):
        c = Client.objects.create(company=self.company, name="Stari naziv")
        url = reverse("client-detail", kwargs={"version": "v1", "pk": c.pk})
        response = self.client.patch(
            url, {"name": "Novi naziv"}, content_type="application/json", **self._headers()
        )
        self.assertEqual(response.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.name, "Novi naziv")

    def test_delete_is_a_soft_delete(self):
        c = Client.objects.create(company=self.company, name="Klijent")
        url = reverse("client-detail", kwargs={"version": "v1", "pk": c.pk})
        response = self.client.delete(url, **self._headers())
        self.assertEqual(response.status_code, 204)

        c.refresh_from_db()
        self.assertFalse(c.is_active)
        # Still there — not actually gone (master prompt §63/§106).
        self.assertTrue(Client.objects.filter(pk=c.pk).exists())


class ClientTenantIsolationTests(TestCase):
    """Master prompt §47: cross-tenant access must be explicitly tested."""

    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)
        self.client_b = Client.objects.create(company=self.company_b, name="Klijent B")
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")

    def test_cannot_use_company_id_header_for_a_company_not_a_member_of(self):
        url = reverse("client-list", kwargs={"version": "v1"})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_b.id))
        self.assertEqual(response.status_code, 403)

    def test_cannot_retrieve_another_companys_client_even_with_own_header(self):
        # Sends its own (valid) company header, but the client pk belongs
        # to a different company entirely.
        url = reverse("client-detail", kwargs={"version": "v1", "pk": self.client_b.pk})
        response = self.client.get(url, HTTP_X_COMPANY_ID=str(self.company_a.id))
        self.assertEqual(response.status_code, 404)


class ClientRbacTests(TestCase):
    """ACCOUNTANT role: view_clients yes, manage_clients no (apps/accounts/permissions.py)."""

    def setUp(self):
        self.accountant_user = User.objects.create_user(
            email="accountant@pausalac.rs", password="s3cr3t-pass"
        )
        self.company = Company.objects.create(name="Firma A")
        Membership.objects.create(
            user=self.accountant_user, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.login(username="accountant@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}

    def test_accountant_can_list_clients(self):
        url = reverse("client-list", kwargs={"version": "v1"})
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_accountant_cannot_create_clients(self):
        url = reverse("client-list", kwargs={"version": "v1"})
        response = self.client.post(url, {"name": "Novi klijent"}, **self.headers)
        self.assertEqual(response.status_code, 403)


class ClientListPaginationTests(TestCase):
    """
    config.pagination.DefaultPagination — added in Phase 2c so the invoice
    form's client picker isn't silently capped at the default page size.
    """

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        self.company = Company.objects.create(name="Firma A")
        Membership.objects.create(user=self.owner, company=self.company)
        Client.objects.bulk_create(
            [Client(company=self.company, name=f"Klijent {i}") for i in range(30)]
        )
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.url = reverse("client-list", kwargs={"version": "v1"})

    def test_default_page_size_is_25(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(len(response.json()["results"]), 25)

    def test_page_size_query_param_is_honored(self):
        response = self.client.get(self.url, {"page_size": 50}, **self.headers)
        self.assertEqual(len(response.json()["results"]), 30)

    def test_page_size_is_capped_at_max(self):
        response = self.client.get(self.url, {"page_size": 500}, **self.headers)
        self.assertEqual(len(response.json()["results"]), 30)  # only 30 exist, cap is 100
