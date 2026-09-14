from rest_framework import mixins, permissions, viewsets

from apps.companies.permissions import HasCompanyPermission

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    List + create only — a recorded payment is never updated or deleted
    (master prompt §63: never silently modify historical financial data;
    a wrong entry needs a correction/refund concept, explicitly deferred
    per §96). Tenant-scoped via the X-Company-Id header, same mechanism
    as apps.clients/apps.invoices.
    """

    serializer_class = PaymentSerializer
    filterset_fields = ["invoice"]
    ordering_fields = ["paid_at", "created_at"]

    def get_permissions(self):
        codename = "record_payment" if self.action == "create" else "view_financial_data"
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return Payment.objects.for_company(self.request.company).select_related("invoice")
