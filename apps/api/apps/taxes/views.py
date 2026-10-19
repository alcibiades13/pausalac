from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.companies.permissions import HasCompanyPermission

from .models import TaxObligation, TaxResolution
from .serializers import TaxObligationSerializer, TaxResolutionSerializer
from .services import TaxService


class TaxResolutionViewSet(viewsets.ModelViewSet):
    """Create + list only — a resolution is immutable once saved (no
    edit/delete endpoint this phase, see docs/decisions-log.md)."""

    serializer_class = TaxResolutionSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        codename = "manage_tax_obligations" if self.action == "create" else "view_financial_data"
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return TaxResolution.objects.for_company(self.request.company)


class TaxObligationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaxObligationSerializer
    filterset_fields = ["status"]
    ordering_fields = ["due_date", "period_start", "status"]

    def get_permissions(self):
        codename = "manage_tax_obligations" if self.action == "mark_paid" else "view_financial_data"
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return TaxObligation.objects.for_company(self.request.company)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None, *args, **kwargs):
        obligation = self.get_object()
        obligation = TaxService.mark_paid(obligation, actor=request.user)
        return Response(self.get_serializer(obligation).data)
