from django.urls import path

from .views import KPOEntryListView, KPOExportPdfView, KPOExportXlsxView

urlpatterns = [
    path("", KPOEntryListView.as_view(), name="kpo-list"),
    path("<int:company_id>/export/pdf/", KPOExportPdfView.as_view(), name="kpo-export-pdf"),
    path("<int:company_id>/export/xlsx/", KPOExportXlsxView.as_view(), name="kpo-export-xlsx"),
]
