from django.contrib import admin

from .models import (
    AccountingConnection,
    AccountingOrganization,
    AccountingOrganizationMembership,
    SyncedMembership,
)


@admin.register(AccountingOrganization)
class AccountingOrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "pib", "contact_email", "created_at")


@admin.register(AccountingOrganizationMembership)
class AccountingOrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "status")
    list_filter = ("role", "status")


@admin.register(AccountingConnection)
class AccountingConnectionAdmin(admin.ModelAdmin):
    list_display = ("organization", "company", "granted_role", "status", "created_at")
    list_filter = ("status", "granted_role")


@admin.register(SyncedMembership)
class SyncedMembershipAdmin(admin.ModelAdmin):
    list_display = ("connection", "membership")
