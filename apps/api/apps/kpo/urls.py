from django.urls import path

from .views import KPOEntryListView, KPOExportPdfView, KPOExportXlsxView, KPOMonthlySummaryView

urlpatterns = [
    path("", KPOEntryListView.as_view(), name="kpo-list"),
    path("monthly-summary/", KPOMonthlySummaryView.as_view(), name="kpo-monthly-summary"),
    path("<int:company_id>/export/pdf/", KPOExportPdfView.as_view(), name="kpo-export-pdf"),
    path("<int:company_id>/export/xlsx/", KPOExportXlsxView.as_view(), name="kpo-export-xlsx"),
]
