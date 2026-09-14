from rest_framework import serializers

from .models import TaxObligation, TaxResolution
from .services import TaxService


class TaxResolutionSerializer(serializers.ModelSerializer):
    rate_check_warnings = serializers.SerializerMethodField()

    class Meta:
        model = TaxResolution
        fields = [
            "id",
            "effective_from",
            "effective_until",
            "tax_base",
            "income_tax_amount",
            "pio_amount",
            "health_amount",
            "unemployment_amount",
            "notes",
            "created_at",
            "rate_check_warnings",
        ]
        read_only_fields = ["id", "created_at", "rate_check_warnings"]

    def get_rate_check_warnings(self, obj: TaxResolution) -> list[str]:
        return TaxService.rate_check_warnings(obj)

    def create(self, validated_data):
        return TaxService.create_resolution(
            company=self.context["request"].company, **validated_data
        )


class TaxObligationSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = TaxObligation
        fields = [
            "id",
            "resolution",
            "period_start",
            "due_date",
            "income_tax_amount",
            "pio_amount",
            "health_amount",
            "unemployment_amount",
            "total_amount",
            "status",
            "paid_at",
        ]
        read_only_fields = fields
