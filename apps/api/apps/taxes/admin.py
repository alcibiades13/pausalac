from django.contrib import admin

from .models import TaxObligation, TaxResolution


@admin.register(TaxResolution)
class TaxResolutionAdmin(admin.ModelAdmin):
    list_display = ("company", "effective_from", "effective_until", "tax_base")


@admin.register(TaxObligation)
class TaxObligationAdmin(admin.ModelAdmin):
    list_display = ("company", "period_start", "due_date", "status", "total_amount")
    list_filter = ("status",)
