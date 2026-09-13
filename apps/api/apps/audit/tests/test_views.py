from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.services import AuditService
from apps.companies.models import Company, Membership


class AuditLogTenantScopingTests(TestCase):
    """
    Exercises the header-based tenant scoping mechanism
    (apps.companies.permissions.resolve_company) — the mechanism future
    domain-resource endpoints (invoices, clients, ...) will reuse, as
    opposed to Company's own URL-based addressing.
    """

    def setUp(self):
        self.owner_a = User.objects.create_user(email="a@pausalac.rs", password="s3cr3t-pass")
        self.owner_b = User.objects.create_user(email="b@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Membership.objects.create(user=self.owner_a, company=self.company_a)
        Membership.objects.create(user=self.owner_b, company=self.company_b)
        AuditService.log(
            actor=self.owner_a,
            company=self.company_a,
            entity_type="company",
            entity_id=self.company_a.id,
            action="created",
        )
        self.client.login(username="a@pausalac.rs", password="s3cr3t-pass")
        self.url = reverse("audit-log-list", kwargs={"version": "v1"})

    def test_missing_company_header_is_rejected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_header_for_company_the_user_is_not_a_member_of_is_rejected(self):
        response = self.client.get(self.url, HTTP_X_COMPANY_ID=str(self.company_b.id))
        self.assertEqual(response.status_code, 403)

    def test_valid_company_header_returns_only_that_companys_entries(self):
        response = self.client.get(self.url, HTTP_X_COMPANY_ID=str(self.company_a.id))
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity_type"], "company")
