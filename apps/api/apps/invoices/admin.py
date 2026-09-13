from django.contrib import admin

from .models import FinancialEvent, Invoice, InvoiceLineItem, InvoiceSequence


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "company", "client", "status", "total", "issue_date")
    list_filter = ("status", "currency")
    search_fields = ("invoice_number", "client__name")
    autocomplete_fields = ["company", "client"]
    inlines = [InvoiceLineItemInline]


@admin.register(InvoiceSequence)
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ("company", "year", "last_number")
    autocomplete_fields = ["company"]


@admin.register(FinancialEvent)
class FinancialEventAdmin(admin.ModelAdmin):
    """Read-only in the admin — the ledger is append-only (like AuditLogEntry)."""

    list_display = ("occurred_at", "company", "event_type", "amount", "currency", "invoice")
    list_filter = ("event_type", "currency")
    autocomplete_fields = ["company", "invoice"]
    date_hierarchy = "occurred_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
