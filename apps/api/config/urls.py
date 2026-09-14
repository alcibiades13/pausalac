"""
URL configuration for the Pausalac backend.

Every domain app under `api/<version>/` is included here as its own
endpoints go live — most domain apps are still empty at this stage (see
docs/implementation-plan.md, Phase 1b vs. later phases).
"""

from django.contrib import admin
from django.urls import include, path

from .health import health, ready

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("companies/", include("apps.companies.urls")),
    path("clients/", include("apps.clients.urls")),
    path("invoices/", include("apps.invoices.urls")),
    path("payments/", include("apps.payments.urls")),
    path("limits/", include("apps.limits.urls")),
    path("kpo/", include("apps.kpo.urls")),
    path("taxes/", include("apps.taxes.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("documents/", include("apps.documents.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("accounting/", include("apps.accounting.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("audit/", include("apps.audit.urls")),
    # In-app admin panel (master prompt §67, Phase 6b) — /api/v1/admin/...,
    # distinct from Django's own admin site mounted at the root /admin/
    # below (no path collision, and Django admin isn't going away).
    path("admin/", include("apps.admin_panel.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
    path("health/ready", ready, name="health-ready"),
    # `version` is captured once here for DRF's URLPathVersioning
    # (REST_FRAMEWORK["DEFAULT_VERSIONING_CLASS"]) and applies to every
    # nested include below.
    path("api/<str:version>/", include(api_v1_patterns)),
]
