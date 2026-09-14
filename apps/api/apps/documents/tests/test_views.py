from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.companies.models import Company, Membership
from apps.taxes.services import TaxService
from apps.taxes.testing import seed_test_rates


def _pdf_file(name="test.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"%PDF-1.4 fake content", content_type="application/pdf")


def _oversized_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("big.pdf", b"0" * (21 * 1024 * 1024), content_type="application/pdf")


class DocumentViewSetTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.owner = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(user=self.owner, company=self.company)
        self.client.login(username="owner@pausalac.rs", password="s3cr3t-pass")
        self.headers = {"HTTP_X_COMPANY_ID": str(self.company.id)}
        self.list_url = reverse("document-list", kwargs={"version": "v1"})

    def test_upload_returns_201_with_file_url(self):
        response = self.client.post(
            self.list_url,
            {"category": "contract", "title": "Ugovor", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertIsNotNone(body["file_url"])
        self.assertEqual(body["original_filename"], "test.pdf")

    def test_oversized_file_rejected(self):
        response = self.client.post(
            self.list_url,
            {
                "category": "contract",
                "title": "Ugovor",
                "description": "",
                "file": _oversized_file(),
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_disallowed_content_type_rejected(self):
        bad_file = SimpleUploadedFile("script.exe", b"MZ", content_type="application/x-msdownload")
        response = self.client.post(
            self.list_url,
            {"category": "contract", "title": "Ugovor", "description": "", "file": bad_file},
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_tax_resolution_from_another_company_rejected(self):
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        seed_test_rates()
        resolution = TaxService.create_resolution(
            other_company,
            effective_from=date(2026, 1, 1),
            effective_until=date(2026, 1, 31),
            tax_base=Decimal("100000.00"),
            income_tax_amount=Decimal("10000.00"),
            pio_amount=Decimal("24000.00"),
            health_amount=Decimal("10300.00"),
            unemployment_amount=Decimal("750.00"),
        )
        response = self.client.post(
            self.list_url,
            {
                "category": "tax_resolution",
                "title": "Rešenje",
                "description": "",
                "file": _pdf_file(),
                "tax_resolution": resolution.id,
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_list_filter_by_category(self):
        self.client.post(
            self.list_url,
            {
                "category": "contract",
                "title": "Ugovor",
                "description": "",
                "file": _pdf_file("a.pdf"),
            },
            **self.headers,
        )
        self.client.post(
            self.list_url,
            {"category": "other", "title": "Ostalo", "description": "", "file": _pdf_file("b.pdf")},
            **self.headers,
        )
        response = self.client.get(self.list_url, {"category": "contract"}, **self.headers)
        self.assertEqual(response.json()["count"], 1)

    def test_search_by_title(self):
        self.client.post(
            self.list_url,
            {"category": "other", "title": "Poseban naziv", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        response = self.client.get(self.list_url, {"search": "Poseban"}, **self.headers)
        self.assertEqual(response.json()["count"], 1)

    def test_accountant_can_view_but_not_upload(self):
        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")

        response = self.client.get(self.list_url, **self.headers)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            self.list_url,
            {"category": "contract", "title": "Ugovor", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_removes_object_from_storage(self):
        upload_response = self.client.post(
            self.list_url,
            {"category": "other", "title": "Test", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        document_id = upload_response.json()["id"]
        from apps.documents.models import Document

        document = Document.objects.get(id=document_id)
        storage = document.file.storage
        name = document.file.name
        self.assertTrue(storage.exists(name))

        detail_url = reverse("document-detail", kwargs={"version": "v1", "pk": document_id})
        response = self.client.delete(detail_url, **self.headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(storage.exists(name))

    def test_accountant_cannot_delete(self):
        upload_response = self.client.post(
            self.list_url,
            {"category": "other", "title": "Test", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        document_id = upload_response.json()["id"]

        accountant = User.objects.create_user(email="acc@pausalac.rs", password="s3cr3t-pass")
        Membership.objects.create(
            user=accountant, company=self.company, role=Membership.Role.ACCOUNTANT
        )
        self.client.logout()
        self.client.login(username="acc@pausalac.rs", password="s3cr3t-pass")

        detail_url = reverse("document-detail", kwargs={"version": "v1", "pk": document_id})
        response = self.client.delete(detail_url, **self.headers)
        self.assertEqual(response.status_code, 403)

    def test_tenant_isolation(self):
        self.client.post(
            self.list_url,
            {"category": "other", "title": "Test", "description": "", "file": _pdf_file()},
            **self.headers,
        )
        other_company = Company.objects.create(name="Firma B", pib="987654321")
        Membership.objects.create(user=self.owner, company=other_company)
        response = self.client.get(self.list_url, HTTP_X_COMPANY_ID=str(other_company.id))
        self.assertEqual(response.json()["count"], 0)
