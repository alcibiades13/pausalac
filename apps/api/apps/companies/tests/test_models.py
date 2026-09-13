from django.test import TestCase

from apps.accounts.models import User
from apps.companies.models import Company, Membership


class TenantScopedManagerTests(TestCase):
    """
    Exercises apps.companies.managers.TenantScopedManager against its first
    real usage (Membership.by_company) — later domain models adopt the same
    manager as their *default* manager (master prompt §47).
    """

    def setUp(self):
        self.user = User.objects.create_user(email="marko@pausalac.rs", password="s3cr3t-pass")
        self.company_a = Company.objects.create(name="Firma A")
        self.company_b = Company.objects.create(name="Firma B")
        Membership.objects.create(user=self.user, company=self.company_a)
        Membership.objects.create(user=self.user, company=self.company_b)

    def test_for_company_only_returns_matching_rows(self):
        scoped = Membership.by_company.for_company(self.company_a)
        self.assertEqual(list(scoped.values_list("company_id", flat=True)), [self.company_a.id])

    def test_for_company_returns_empty_for_unrelated_company(self):
        other_company = Company.objects.create(name="Firma C")
        scoped = Membership.by_company.for_company(other_company)
        self.assertEqual(scoped.count(), 0)
