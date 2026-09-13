"""
URL configuration for the Pausalac backend.

Domain apps will each own a `urls.py` and get included here under
`api/v1/<domain>/` once they expose endpoints (none do yet at the
bootstrap stage — see docs/implementation-plan.md, Phase 1a).
"""

from django.contrib import admin
from django.urls import path

from .health import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
]
