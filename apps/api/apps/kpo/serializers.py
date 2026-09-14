from rest_framework import serializers

from .models import KPOEntry


class KPOEntrySerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = KPOEntry
        fields = [
            "id",
            "sequence_number",
            "entry_date",
            "description",
            "product_revenue",
            "service_revenue",
            "total_revenue",
            "entry_type",
        ]
        read_only_fields = fields
