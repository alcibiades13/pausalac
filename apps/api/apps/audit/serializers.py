from rest_framework import serializers

from .models import AuditLogEntry


class AuditLogEntrySerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, default=None)

    class Meta:
        model = AuditLogEntry
        fields = [
            "id",
            "actor_email",
            "entity_type",
            "entity_id",
            "action",
            "old_value",
            "new_value",
            "source",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields
