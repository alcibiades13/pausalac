from django.contrib import admin

from .models import Company, Membership


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "pib", "country", "is_active", "created_at")
    search_fields = ("name", "legal_name", "pib")
    list_filter = ("is_active", "country")
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "status", "created_at")
    list_filter = ("role", "status")
    search_fields = ("user__email", "company__name")
    autocomplete_fields = ["user", "company", "invited_by"]
