from rest_framework import serializers

from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "identifier",
            "name",
            "price",
            "currency",
            "billing_interval",
            "entitlements",
        ]
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "status",
            "plan",
            "trial_ends_at",
            "price_snapshot",
            "current_period_end",
            "cancelled_at",
        ]
        read_only_fields = fields


class ActivatePlanSerializer(serializers.Serializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.filter(is_active=True))
