from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "recipient",
        "event_type",
        "priority",
        "channel",
        "status",
        "created_at",
    )
    list_filter = ("priority", "channel", "status")
