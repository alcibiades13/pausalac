from django.test import TestCase

from apps.clients.models import Client
from apps.companies.models import Company
from apps.companies.onboarding import compute_onboarding_status


class ComputeOnboardingStatusTests(TestCase):
    def test_brand_new_company_has_only_the_default_percentage(self):
        company = Company.objects.create(name="Firma A")
        status = compute_onboarding_status(company)
        self.assertEqual(status["completed"], [])
        self.assertIn("company", status["missing"])
        self.assertIn("bank", status["missing"])
        self.assertIn("client", status["missing"])

    def test_percentage_increases_as_fields_fill_in(self):
        company = Company.objects.create(name="Firma A", pib="123456789", bank_account="RS35...")
        Client.objects.create(company=company, name="Klijent A")
        status = compute_onboarding_status(company)
        self.assertEqual(set(status["completed"]), {"company", "bank", "client"})
        self.assertEqual(status["percentage"], 60)  # 3 of 5 tracked items

    def test_inactive_clients_do_not_count(self):
        company = Company.objects.create(name="Firma A")
        Client.objects.create(company=company, name="Klijent A", is_active=False)
        status = compute_onboarding_status(company)
        self.assertIn("client", status["missing"])

    def test_sef_and_tax_document_are_always_missing_for_now(self):
        company = Company.objects.create(name="Firma A", pib="123456789", bank_account="RS35...")
        Client.objects.create(company=company, name="Klijent A")
        status = compute_onboarding_status(company)
        self.assertIn("sef", status["missing"])
        self.assertIn("tax_document", status["missing"])
