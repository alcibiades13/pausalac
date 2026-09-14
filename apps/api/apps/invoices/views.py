from django.http import HttpResponse
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.companies.models import Membership
from apps.companies.permissions import HasCompanyPermission

from .models import Invoice
from .pdf import render_invoice_pdf
from .serializers import InvoiceSerializer
from .services import InvalidTransitionError, InvoiceService
from .tasks import send_invoice_email_task


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Tenant-scoped via the X-Company-Id header (apps.companies.permissions),
    same mechanism as apps.clients. Editing is DRAFT-only (enforced in
    InvoiceService.update_draft); status changes only happen through the
    issue/cancel/send actions, never a generic PATCH of `status` (master
    prompt §11).

    The `pdf` action is the one exception to the header-based scoping:
    a plain <a href> download can't set a custom header, so it resolves
    tenancy from the invoice's own company instead — same idea as
    CompanyViewSet addressing Company directly by id (apps/companies/views.py).
    """

    serializer_class = InvoiceSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["status", "client"]
    search_fields = ["invoice_number", "notes"]
    ordering_fields = ["issue_date", "due_date", "created_at"]

    def get_permissions(self):
        if self.action == "pdf":
            return [permissions.IsAuthenticated()]
        codename = {
            "list": "view_financial_data",
            "retrieve": "view_financial_data",
            "create": "create_invoice",
            "update": "edit_invoice",
            "partial_update": "edit_invoice",
            "issue": "edit_invoice",
            "send": "edit_invoice",
            "cancel": "cancel_invoice",
        }[self.action]
        gates = [permissions.IsAuthenticated(), HasCompanyPermission(codename)()]
        if self.action == "create":
            # Phase 5's one real entitlement-enforcement point (master
            # prompt §104: "backend must enforce") — added alongside the
            # RBAC check above, not instead of it. Deliberately not swept
            # across every other write endpoint this phase; see
            # docs/decisions-log.md. Lazy import: apps.subscriptions sits
            # after apps.invoices in DOMAIN_APPS.
            from apps.subscriptions.permissions import HasActiveSubscription

            gates.append(HasActiveSubscription())
        return gates

    def get_queryset(self):
        base = Invoice.objects.select_related("client", "company").prefetch_related("items")
        if self.action == "pdf":
            user = self.request.user
            if user.is_superuser:
                return base
            return base.filter(
                company__memberships__user=user,
                company__memberships__status=Membership.Status.ACTIVE,
            ).distinct()
        return base.for_company(self.request.company)

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

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None, *args, **kwargs):
        invoice = self.get_object()
        if not request.user.has_company_permission(invoice.company, "view_financial_data"):
            raise exceptions.PermissionDenied("Nemate dozvolu da vidite ovu fakturu.")
        pdf_bytes = render_invoice_pdf(invoice)
        filename = invoice.invoice_number or f"nacrt-{invoice.id}"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}.pdf"'
        return response

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != Invoice.Status.ISSUED:
            raise exceptions.ValidationError(
                "Samo izdata faktura može da se pošalje klijentu."
            )
        recipient_email = request.data.get("recipient_email") or invoice.client.email
        if not recipient_email:
            raise exceptions.ValidationError(
                {"recipient_email": "Klijent nema email adresu — unesi je ručno."}
            )
        message = request.data.get("message", "")
        send_invoice_email_task.delay(invoice.id, recipient_email, message, request.user.id)
        return Response({"detail": "Faktura se šalje."}, status=202)
