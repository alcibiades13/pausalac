from rest_framework import serializers

from .models import Invoice, InvoiceLineItem
from .services import InvalidTransitionError, InvoiceService


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = [
            "id",
            "description",
            "item_type",
            "quantity",
            "unit_price",
            "line_total",
            "position",
        ]
        read_only_fields = ["id", "line_total", "position"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceLineItemSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)
    client_email = serializers.CharField(source="client.email", read_only=True)
    converted_from_number = serializers.CharField(
        source="converted_from.invoice_number", read_only=True, default=None
    )
    converted_to = serializers.SerializerMethodField()
    converted_to_number = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "client",
            "client_name",
            "client_email",
            "invoice_number",
            "status",
            "document_type",
            "converted_from",
            "converted_from_number",
            "converted_to",
            "converted_to_number",
            "issue_date",
            "due_date",
            "service_date",
            "currency",
            "total",
            "notes",
            "issued_at",
            "sent_at",
            "paid_at",
            "cancelled_at",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "status",
            "converted_from",
            "total",
            "issued_at",
            "sent_at",
            "paid_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]

    def get_converted_to(self, invoice):
        # At most one conversion is ever created (InvoiceService.
        # convert_to_invoice refuses a second one) — .first() is enough.
        converted = invoice.conversions.first()
        return converted.id if converted else None

    def get_converted_to_number(self, invoice):
        converted = invoice.conversions.first()
        return converted.invoice_number if converted else None

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
        if (
            self.instance is not None
            and "document_type" in attrs
            and attrs["document_type"] != self.instance.document_type
        ):
            raise serializers.ValidationError(
                {"document_type": "Tip dokumenta ne može da se menja nakon kreiranja."}
            )
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
