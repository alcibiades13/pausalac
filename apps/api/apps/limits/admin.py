from django.contrib import admin

from .models import RegulatoryRule


@admin.register(RegulatoryRule)
class RegulatoryRuleAdmin(admin.ModelAdmin):
    """Internal/ops editing only — no tenant-facing rules-management
    endpoint yet (§25's versioning discipline doesn't require a full UI
    to be honored, just a single non-hardcoded source of truth)."""

    list_display = ("identifier", "version", "effective_from", "effective_until", "approval_status")
    list_filter = ("identifier", "approval_status")
    ordering = ("identifier", "-effective_from", "-version")
