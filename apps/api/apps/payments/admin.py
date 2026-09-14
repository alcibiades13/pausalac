from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Read-only-ish in the admin — no delete, matching §63 (no update UI here either)."""

    list_display = ("invoice", "company", "amount", "currency", "method", "paid_at", "created_at")
    list_filter = ("method", "currency")
    search_fields = ("invoice__invoice_number",)
    autocomplete_fields = ["company", "invoice"]

    def has_delete_permission(self, request, obj=None):
        return False
