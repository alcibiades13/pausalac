from rest_framework import generics, permissions

from apps.companies.permissions import HasCompanyPermission

from .models import AuditLogEntry
from .serializers import AuditLogEntrySerializer


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/v1/audit/ — audit trail for the company resolved from the
    X-Company-Id header (apps.companies.permissions.resolve_company),
    gated by the `view_audit` permission. No write endpoints exist here —
    the audit log is append-only and only ever written by AuditService.
    """

    serializer_class = AuditLogEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_audit")]
    filterset_fields = ["entity_type", "action", "source"]
    search_fields = ["entity_type", "entity_id", "action"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return AuditLogEntry.objects.filter(company=self.request.company)
