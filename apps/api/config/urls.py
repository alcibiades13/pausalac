"""
URL configuration for the Pausalac backend.

Every domain app under `api/<version>/` is included here as its own
endpoints go live — most domain apps are still empty at this stage (see
docs/implementation-plan.md, Phase 1b vs. later phases).
"""

from django.contrib import admin
from django.urls import include, path

from .health import health

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("companies/", include("apps.companies.urls")),
    path("clients/", include("apps.clients.urls")),
    path("invoices/", include("apps.invoices.urls")),
    path("payments/", include("apps.payments.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("audit/", include("apps.audit.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
    # `version` is captured once here for DRF's URLPathVersioning
    # (REST_FRAMEWORK["DEFAULT_VERSIONING_CLASS"]) and applies to every
    # nested include below.
    path("api/<str:version>/", include(api_v1_patterns)),
]
