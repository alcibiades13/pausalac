from rest_framework import serializers

from apps.companies.models import Membership

from .models import AccountingConnection, AccountingOrganization, AccountingOrganizationMembership
from .services import AccountingService

GRANTED_ROLE_CHOICES = [
    (Membership.Role.ACCOUNTANT, Membership.Role.ACCOUNTANT.label),
    (Membership.Role.ACCOUNTANT_ADMIN, Membership.Role.ACCOUNTANT_ADMIN.label),
]


class AccountingOrganizationSerializer(serializers.ModelSerializer):
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = AccountingOrganization
        fields = ["id", "name", "contact_email", "pib", "created_at", "my_role"]
        read_only_fields = ["id", "created_at", "my_role"]

    def get_my_role(self, obj: AccountingOrganization) -> str | None:
        request = self.context.get("request")
        if request is None:
            return None
        membership = obj.staff_memberships.filter(
            user=request.user, status=AccountingOrganizationMembership.Status.ACTIVE
        ).first()
        return membership.role if membership else None

    def create(self, validated_data):
        return AccountingService.create_organization(
            self.context["request"].user, **validated_data
        )


class AccountingOrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = AccountingOrganizationMembership
        fields = ["id", "user", "user_email", "organization", "role", "status", "created_at"]
        read_only_fields = ["id", "user", "user_email", "organization", "status", "created_at"]


class AccountingOrganizationMembershipCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=AccountingOrganizationMembership.Role.choices)


class AccountingConnectionCreateSerializer(serializers.Serializer):
    """Org-side: invite an existing client company by PIB."""

    company_pib = serializers.CharField()
    granted_role = serializers.ChoiceField(choices=GRANTED_ROLE_CHOICES)


class OrganizationConnectionSerializer(serializers.ModelSerializer):
    """Org-side listing: which client companies this org is connected to."""

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_pib = serializers.CharField(source="company.pib", read_only=True)

    class Meta:
        model = AccountingConnection
        fields = [
            "id",
            "company",
            "company_name",
            "company_pib",
            "granted_role",
            "status",
            "created_at",
            "accepted_at",
            "revoked_at",
        ]
        read_only_fields = fields


class ClientConnectionSerializer(serializers.ModelSerializer):
    """Client-side listing ("Moj računovođa"): which accounting orgs are
    connected to the current company."""

    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = AccountingConnection
        fields = [
            "id",
            "organization",
            "organization_name",
            "granted_role",
            "status",
            "created_at",
            "accepted_at",
            "revoked_at",
        ]
        read_only_fields = fields
