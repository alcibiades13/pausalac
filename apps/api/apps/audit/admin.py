from django.contrib import admin

from .models import AuditLogEntry


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    """Read-only in the admin — audit entries are append-only (§22)."""

    list_display = (
        "created_at",
        "actor",
        "company",
        "entity_type",
        "entity_id",
        "action",
        "source",
    )
    list_filter = ("source", "entity_type")
    search_fields = ("entity_type", "entity_id", "action")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
