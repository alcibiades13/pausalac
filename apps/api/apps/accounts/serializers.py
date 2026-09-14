from django.contrib.auth import password_validation
from rest_framework import serializers

from apps.companies.serializers import MyMembershipSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def validate_email(self, value: str) -> str:
        value = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Nalog sa ovom email adresom već postoji.")
        return value

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class MeSerializer(serializers.ModelSerializer):
    memberships = MyMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_email_verified",
            "is_staff",
            "memberships",
        ]
        # is_staff is a real writable model field (unlike is_email_verified,
        # a property) — read-only here so this serializer stays safe if it's
        # ever reused for a profile-update endpoint (it's output-only today).
        read_only_fields = ["is_staff"]


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    # Password strength is validated in the view, once the token has been
    # resolved to a concrete user (so UserAttributeSimilarityValidator has
    # something to compare against) — see AccountsViews.PasswordResetConfirmView.
