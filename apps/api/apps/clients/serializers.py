from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "client_type",
            "name",
            "tax_id",
            "email",
            "phone",
            "address",
            "country",
            "default_currency",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClientSummarySerializer(serializers.Serializer):
    """Master prompt §15/blueprint §6.3 client-profile totals — see
    apps.clients.services.ClientService.compute_summary. A plain
    Serializer (not tied to the model) so the money fields serialize as
    strings like every other amount in the API, not raw JSON floats."""

    total_invoiced = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=14, decimal_places=2)
    outstanding = serializers.DecimalField(max_digits=14, decimal_places=2)
    invoice_count = serializers.IntegerField()
    last_invoice_date = serializers.DateField(allow_null=True)
