from django.db.utils import IntegrityError
from django.test import TestCase

from apps.clients.models import Client
from apps.companies.models import Company


class ClientTenantScopingTests(TestCase):
    """Client.objects is TenantScopedManager by default — the first domain
    model to prove out that Phase 1b pattern for real."""

    def setUp(self):
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Client.objects.create(company=self.company_a, name="Klijent A1")
        Client.objects.create(company=self.company_a, name="Klijent A2")
        Client.objects.create(company=self.company_b, name="Klijent B1")

    def test_for_company_only_returns_matching_rows(self):
        clients = Client.objects.for_company(self.company_a)
        self.assertEqual(clients.count(), 2)
        self.assertTrue(all(c.company_id == self.company_a.id for c in clients))

    def test_for_company_returns_empty_for_company_with_no_clients(self):
        other = Company.objects.create(name="Firma C")
        self.assertEqual(Client.objects.for_company(other).count(), 0)


class ClientModelTests(TestCase):
    def test_blank_name_is_rejected_at_database_level(self):
        company = Company.objects.create(name="Firma A")
        with self.assertRaises(IntegrityError):
            Client.objects.create(company=company, name="")
