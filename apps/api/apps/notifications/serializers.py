from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "event_type",
            "priority",
            "title",
            "message",
            "action_route",
            "action_query",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields
