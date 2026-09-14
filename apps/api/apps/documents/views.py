from rest_framework import permissions, viewsets

from apps.companies.permissions import HasCompanyPermission

from .models import Document
from .serializers import DocumentSerializer
from .services import DocumentService


class DocumentViewSet(viewsets.ModelViewSet):
    """No update — a document is delete-and-reupload only, same
    immutable stance as TaxResolution (Phase 3c)."""

    serializer_class = DocumentSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]
    filterset_fields = ["category", "tax_resolution"]
    search_fields = ["title", "description", "original_filename"]

    def get_permissions(self):
        codename = "upload_documents" if self.action in ("create", "destroy") else "view_documents"
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return Document.objects.for_company(self.request.company)

    def perform_destroy(self, instance):
        DocumentService.delete(instance, actor=self.request.user)
