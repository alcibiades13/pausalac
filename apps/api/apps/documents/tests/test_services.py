from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.accounts.models import User
from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.services import DocumentService


def _pdf_file(name="test.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"%PDF-1.4 fake content", content_type="application/pdf")


class DocumentServiceUploadTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")

    def test_upload_creates_document_with_snapshotted_metadata(self):
        document = DocumentService.upload(
            self.company,
            uploaded_by=self.user,
            category=Document.Category.CONTRACT,
            title="Ugovor sa klijentom",
            description="",
            file_obj=_pdf_file(),
        )
        self.assertEqual(document.original_filename, "test.pdf")
        self.assertEqual(document.content_type, "application/pdf")
        self.assertGreater(document.size_bytes, 0)
        self.assertEqual(document.company, self.company)
        self.assertEqual(document.uploaded_by, self.user)


class DocumentServiceDeleteTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Firma A", pib="123456789")
        self.user = User.objects.create_user(email="owner@pausalac.rs", password="s3cr3t-pass")

    def test_delete_removes_row_and_storage_object(self):
        document = DocumentService.upload(
            self.company,
            uploaded_by=self.user,
            category=Document.Category.OTHER,
            title="Test",
            description="",
            file_obj=_pdf_file(),
        )
        storage = document.file.storage
        name = document.file.name
        self.assertTrue(storage.exists(name))

        document_id = document.id
        DocumentService.delete(document, actor=self.user)

        self.assertFalse(storage.exists(name))
        self.assertFalse(Document.objects.filter(id=document_id).exists())
