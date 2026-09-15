from rest_framework import serializers

from .models import Document
from .services import DocumentService

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "category",
            "title",
            "description",
            "file",
            "file_url",
            "original_filename",
            "content_type",
            "size_bytes",
            "tax_resolution",
            "client",
            "invoice",
            "payment",
            "tax_obligation",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "file_url",
            "original_filename",
            "content_type",
            "size_bytes",
            "uploaded_by_name",
            "created_at",
        ]

    def get_file_url(self, obj: Document) -> str | None:
        return obj.file.url if obj.file else None

    def get_uploaded_by_name(self, obj: Document) -> str:
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else ""

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError("Fajl je prevelik (maksimalno 20MB).")
        if value.content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError("Nepodržan tip fajla.")
        return value

    def validate_tax_resolution(self, value):
        request = self.context["request"]
        if value is not None and value.company_id != request.company.id:
            raise serializers.ValidationError("Poresko rešenje ne pripada ovoj kompaniji.")
        return value

    def validate_client(self, value):
        request = self.context["request"]
        if value is not None and value.company_id != request.company.id:
            raise serializers.ValidationError("Klijent ne pripada ovoj kompaniji.")
        return value

    def validate_invoice(self, value):
        request = self.context["request"]
        if value is not None and value.company_id != request.company.id:
            raise serializers.ValidationError("Faktura ne pripada ovoj kompaniji.")
        return value

    def validate_payment(self, value):
        request = self.context["request"]
        if value is not None and value.company_id != request.company.id:
            raise serializers.ValidationError("Uplata ne pripada ovoj kompaniji.")
        return value

    def validate_tax_obligation(self, value):
        request = self.context["request"]
        if value is not None and value.company_id != request.company.id:
            raise serializers.ValidationError("Poreska obaveza ne pripada ovoj kompaniji.")
        return value

    def create(self, validated_data):
        file_obj = validated_data.pop("file")
        return DocumentService.upload(
            company=self.context["request"].company,
            uploaded_by=self.context["request"].user,
            file_obj=file_obj,
            **validated_data,
        )
