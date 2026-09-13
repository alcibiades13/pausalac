from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "client_type", "email", "is_active", "created_at")
    list_filter = ("client_type", "is_active", "country")
    search_fields = ("name", "tax_id", "email")
    autocomplete_fields = ["company"]
