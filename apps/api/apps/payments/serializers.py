from rest_framework import serializers

from .models import Payment
from .services import InvalidPaymentError, PaymentService


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "amount",
            "currency",
            "paid_at",
            "method",
            "notes",
            "idempotency_key",
            "created_at",
        ]
        read_only_fields = ["id", "currency", "created_at"]
        extra_kwargs = {"idempotency_key": {"write_only": True, "required": False}}

    def validate_invoice(self, value):
        # invoice.company isn't scoped by TenantScopedManager's default
        # queryset by itself — same gap InvoiceSerializer.validate_client
        # closes for Invoice/Client (apps/invoices/serializers.py).
        request = self.context["request"]
        if value.company_id != request.company.id:
            raise serializers.ValidationError("Faktura ne pripada ovoj kompaniji.")
        return value

    def create(self, validated_data):
        try:
            return PaymentService.record_payment(
                validated_data["invoice"],
                amount=validated_data["amount"],
                paid_at=validated_data["paid_at"],
                method=validated_data.get("method", Payment.Method.BANK_TRANSFER),
                notes=validated_data.get("notes", ""),
                actor=self.context["request"].user,
                idempotency_key=validated_data.get("idempotency_key", ""),
            )
        except InvalidPaymentError as exc:
            raise serializers.ValidationError(str(exc)) from exc
