from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.companies.permissions import HasCompanyPermission

from .models import Invoice
from .serializers import InvoiceSerializer
from .services import InvalidTransitionError, InvoiceService


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Tenant-scoped via the X-Company-Id header (apps.companies.permissions),
    same mechanism as apps.clients. Editing is DRAFT-only (enforced in
    InvoiceService.update_draft); status changes only happen through the
    issue/cancel actions, never a generic PATCH of `status` (master
    prompt §11).
    """

    serializer_class = InvoiceSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "client"]
    search_fields = ["invoice_number", "notes"]
    ordering_fields = ["issue_date", "due_date", "created_at"]

    def get_permissions(self):
        codename = {
            "list": "view_financial_data",
            "retrieve": "view_financial_data",
            "create": "create_invoice",
            "update": "edit_invoice",
            "partial_update": "edit_invoice",
            "issue": "edit_invoice",
            "cancel": "cancel_invoice",
        }[self.action]
        return [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]

    def get_queryset(self):
        return (
            Invoice.objects.for_company(self.request.company)
            .select_related("client")
            .prefetch_related("items")
        )

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None, *args, **kwargs):
        invoice = self.get_object()
        try:
            invoice = InvoiceService.issue(invoice, actor=request.user)
        except InvalidTransitionError as exc:
            raise exceptions.ValidationError(str(exc)) from exc
        return Response(self.get_serializer(invoice).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None, *args, **kwargs):
        invoice = self.get_object()
        try:
            invoice = InvoiceService.cancel(invoice, actor=request.user)
        except InvalidTransitionError as exc:
            raise exceptions.ValidationError(str(exc)) from exc
        return Response(self.get_serializer(invoice).data)
