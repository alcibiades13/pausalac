from django.contrib import admin

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "price", "currency", "billing_interval", "is_active")
    list_filter = ("is_active", "billing_interval")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("company", "status", "plan", "trial_ends_at", "current_period_end")
    list_filter = ("status", "plan")
    autocomplete_fields = ("company",)
