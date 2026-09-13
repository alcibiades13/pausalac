from rest_framework import permissions, viewsets

from apps.audit.services import AuditService
from apps.companies.permissions import HasCompanyPermission

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    Tenant-scoped via the X-Company-Id header (apps.companies.permissions),
    the same mechanism apps.audit.views.AuditLogListView already uses —
    Client is the first *writable* resource proving that pattern out.
    """

    serializer_class = ClientSerializer
    filterset_fields = ["client_type", "is_active"]
    search_fields = ["name", "tax_id", "email"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        codename = "view_clients" if self.action in ("list", "retrieve") else "manage_clients"
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return Client.objects.for_company(self.request.company).order_by("name")

    def perform_create(self, serializer):
        client = serializer.save(company=self.request.company)
        AuditService.log(
            actor=self.request.user,
            company=self.request.company,
            entity_type="client",
            entity_id=client.id,
            action="created",
            new_value=ClientSerializer(client).data,
        )

    def perform_update(self, serializer):
        old_value = ClientSerializer(serializer.instance).data
        client = serializer.save()
        AuditService.log(
            actor=self.request.user,
            company=self.request.company,
            entity_type="client",
            entity_id=client.id,
            action="updated",
            old_value=old_value,
            new_value=ClientSerializer(client).data,
        )

    def perform_destroy(self, instance):
        # Soft delete only — master prompt §63/§106: never silently lose
        # historical data. A deactivated client's past invoices (once that
        # domain exists) must still resolve correctly.
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        AuditService.log(
            actor=self.request.user,
            company=self.request.company,
            entity_type="client",
            entity_id=instance.id,
            action="deactivated",
        )
