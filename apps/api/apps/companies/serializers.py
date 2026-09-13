from rest_framework import serializers

from .models import Company, Membership


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "legal_name",
            "pib",
            "address",
            "city",
            "country",
            "activity_code",
            "default_currency",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_email",
            "company",
            "role",
            "status",
            "invited_by",
            "created_at",
            "revoked_at",
        ]
        read_only_fields = ["id", "company", "invited_by", "created_at", "revoked_at"]


class MyMembershipSerializer(serializers.ModelSerializer):
    """Used on /auth/me/ — the company's own data alongside the caller's role in it."""

    company = CompanySerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["company", "role", "status"]
