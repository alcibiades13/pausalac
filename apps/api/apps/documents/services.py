"""
Document upload/delete business logic — mirrors the *Service shape used
across every other domain (master prompt §112: views stay thin).
"""

from apps.audit.services import AuditService

from .models import Document


class DocumentService:
    @staticmethod
    def upload(
        company,
        *,
        uploaded_by,
        category: str,
        title: str,
        description: str,
        file_obj,
        tax_resolution=None,
    ) -> Document:
        document = Document.objects.create(
            company=company,
            uploaded_by=uploaded_by,
            category=category,
            title=title,
            description=description,
            file=file_obj,
            original_filename=file_obj.name,
            content_type=file_obj.content_type,
            size_bytes=file_obj.size,
            tax_resolution=tax_resolution,
        )
        AuditService.log(
            actor=uploaded_by,
            company=company,
            entity_type="document",
            entity_id=document.id,
            action="uploaded",
            new_value={"category": document.category, "title": document.title},
        )
        # Lazy import — apps.analytics sits after apps.documents in DOMAIN_APPS.
        from apps.analytics.tracking import track_event

        track_event(
            "document_uploaded", user=uploaded_by, company=company, category=document.category
        )
        return document

    @staticmethod
    def delete(document: Document, actor) -> None:
        # Delete the storage object first — a deleted Document row must
        # never leave an orphaned object in the bucket.
        document.file.delete(save=False)
        AuditService.log(
            actor=actor,
            company=document.company,
            entity_type="document",
            entity_id=document.id,
            action="deleted",
            old_value={"category": document.category, "title": document.title},
        )
        document.delete()
