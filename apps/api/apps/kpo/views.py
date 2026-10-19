from datetime import date

from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.models import Company, Membership
from apps.companies.permissions import HasCompanyPermission

from .excel import render_kpo_excel
from .models import KPOEntry
from .pdf import render_kpo_pdf
from .serializers import KPOEntrySerializer
from .services import monthly_summary


class KPOEntryListView(generics.ListAPIView):
    """Tenant-scoped via the X-Company-Id header, same mechanism as
    Invoices/Clients/Payments/Limits."""

    serializer_class = KPOEntrySerializer
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]
    ordering_fields = ["entry_date", "sequence_number", "created_at"]
    # description is auto-generated per entry as "Faktura <broj> — <klijent>"
    # (apps.kpo.services), so it's genuinely distinct per row and worth
    # searching, unlike e.g. entry_type (two fixed values only).
    search_fields = ["description"]

    def get_queryset(self):
        queryset = KPOEntry.objects.for_company(self.request.company)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        return queryset


class KPOMonthlySummaryView(APIView):
    """Aggregate for `KpoMonthlyBarChart` — a thin wrapper over
    `apps.kpo.services.monthly_summary`, not a second implementation of
    KPO totals (the same `KPOEntry` rows the table itself lists)."""

    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get(self, request, *args, **kwargs):
        raw_year = request.query_params.get("year")
        try:
            year = int(raw_year) if raw_year else date.today().year
        except ValueError:
            raise ValidationError({"year": ["Unesite ispravnu godinu."]}) from None
        return Response(monthly_summary(request.company, year))


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
