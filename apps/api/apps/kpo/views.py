from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView

from apps.companies.models import Company, Membership
from apps.companies.permissions import HasCompanyPermission

from .excel import render_kpo_excel
from .models import KPOEntry
from .pdf import render_kpo_pdf
from .serializers import KPOEntrySerializer


class KPOEntryListView(generics.ListAPIView):
    """Tenant-scoped via the X-Company-Id header, same mechanism as
    Invoices/Clients/Payments/Limits."""

    serializer_class = KPOEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get_queryset(self):
        queryset = KPOEntry.objects.for_company(self.request.company)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        return queryset


def _company_for_export(request, company_id) -> Company:
    """Own-id addressed, like InvoiceViewSet.pdf (Phase 2d) — a plain
    <a href> download can't set X-Company-Id. Membership-filtered
    queryset means a non-member gets 404, not 403 (established
    tenant-detail-access convention, apps/companies/views.py)."""
    company = (
        Company.objects.filter(
            memberships__user=request.user, memberships__status=Membership.Status.ACTIVE
        )
        .distinct()
        .filter(pk=company_id)
        .first()
    )
    if company is None:
        raise NotFound()
    if not request.user.has_company_permission(company, "view_financial_data"):
        raise PermissionDenied("Nemate dozvolu da vidite KPO ove kompanije.")
    return company


class KPOExportPdfView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_id, *args, **kwargs):
        company = _company_for_export(request, company_id)
        entries = KPOEntry.objects.for_company(company)
        pdf_bytes = render_kpo_pdf(company, entries)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="kpo.pdf"'
        return response


class KPOExportXlsxView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_id, *args, **kwargs):
        company = _company_for_export(request, company_id)
        entries = KPOEntry.objects.for_company(company)
        xlsx_bytes = render_kpo_excel(company, entries)
        response = HttpResponse(
            xlsx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="kpo.xlsx"'
        return response
