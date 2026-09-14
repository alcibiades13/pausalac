from django.contrib import admin

from .models import KPOEntry, KPOSequence


@admin.register(KPOEntry)
class KPOEntryAdmin(admin.ModelAdmin):
    list_display = ("company", "sequence_number", "entry_date", "entry_type", "total_revenue")
    list_filter = ("entry_type",)
    ordering = ("company", "sequence_number")


@admin.register(KPOSequence)
class KPOSequenceAdmin(admin.ModelAdmin):
    list_display = ("company", "year", "last_number")
