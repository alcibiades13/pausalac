from rest_framework import serializers

from .models import Invoice, InvoiceLineItem
from .services import InvalidTransitionError, InvoiceService


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ["id", "description", "quantity", "unit_price", "line_total", "position"]
        read_only_fields = ["id", "line_total", "position"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceLineItemSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "client",
            "client_name",
            "invoice_number",
            "status",
            "issue_date",
            "due_date",
            "service_date",
            "currency",
            "total",
            "notes",
            "issued_at",
            "cancelled_at",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "status",
            "total",
            "issued_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

    def validate_client(self, value):
        # A PrimaryKeyRelatedField's default queryset (Client.objects.all())
        # isn't tenant-scoped by itself — without this, a user could link
        # an invoice to another company's client by guessing its id
        # (master prompt §47).
        request = self.context["request"]
        if value.company_id != request.company.id:
            raise serializers.ValidationError("Klijent ne pripada ovoj kompaniji.")
        return value

    def validate(self, attrs):
        items = attrs.get("items")
        if self.instance is None and not items:
            raise serializers.ValidationError({"items": "Faktura mora imati bar jednu stavku."})
        if items is not None and len(items) == 0:
            raise serializers.ValidationError({"items": "Faktura mora imati bar jednu stavku."})
        return attrs

    def create(self, validated_data):
        line_items = validated_data.pop("items")
        client = validated_data.pop("client")
        return InvoiceService.create_draft(
            company=self.context["request"].company,
            client=client,
            line_items=line_items,
            **validated_data,
        )

    def update(self, instance, validated_data):
        line_items = validated_data.pop("items", None)
        try:
            return InvoiceService.update_draft(instance, line_items=line_items, **validated_data)
        except InvalidTransitionError as exc:
            raise serializers.ValidationError(str(exc)) from exc
