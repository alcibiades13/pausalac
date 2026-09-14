from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("company", "category", "title", "uploaded_by", "created_at")
    list_filter = ("category",)
