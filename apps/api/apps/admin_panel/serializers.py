"""
Admin-facing serializers (master prompt §67). Each cross-tenant variant
adds a company_id/company_name the tenant-scoped original never needed
(a normal caller already knows their own company from the X-Company-Id
header) — everything else is reused as-is.
"""

from rest_framework import serializers

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry
from apps.documents.models import Document
from apps.invoices.models import Invoice
from apps.limits.models import RegulatoryRule
from apps.notifications.models import Notification
from apps.subscriptions.models import Plan, Subscription
from apps.subscriptions.serializers import PlanSerializer
from apps.taxes.models import TaxObligation


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "email_verified_at",
        ]
        read_only_fields = fields


class AdminSubscriptionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "company_id",
            "company_name",
            "status",
            "plan",
            "trial_ends_at",
            "price_snapshot",
            "current_period_end",
            "cancelled_at",
        ]
        read_only_fields = fields


class AdminPlanSerializer(serializers.ModelSerializer):
    """Writable, unlike the client-facing PlanSerializer (apps.subscriptions)
    — the whole point of Plan CRUD living here (master prompt §50: "do not
    hard-code prices into frontend" means prices must be editable
    somewhere without a deploy)."""

    class Meta:
        model = Plan
        fields = [
            "id",
            "identifier",
            "name",
            "price",
            "currency",
            "billing_interval",
            "entitlements",
            "is_active",
        ]
        read_only_fields = ["id"]


class AdminInvoiceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "company_id",
            "company_name",
            "client_name",
            "invoice_number",
            "status",
            "issue_date",
            "due_date",
            "total",
            "currency",
            "created_at",
        ]
        read_only_fields = fields


class AdminDocumentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    uploaded_by_email = serializers.EmailField(
        source="uploaded_by.email", read_only=True, default=None
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "company_id",
            "company_name",
            "category",
            "title",
            "original_filename",
            "size_bytes",
            "uploaded_by_email",
            "created_at",
        ]
        read_only_fields = fields


class AdminTaxObligationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = TaxObligation
        fields = [
            "id",
            "company_id",
            "company_name",
            "period_start",
            "due_date",
            "total_amount",
            "status",
            "paid_at",
        ]
        read_only_fields = fields


class AdminRegulatoryRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryRule
        fields = [
            "id",
            "identifier",
            "config",
            "effective_from",
            "effective_until",
            "source",
            "version",
            "approval_status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approval_status", "created_at"]


class AdminNotificationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    recipient_email = serializers.EmailField(source="recipient.email", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "company_id",
            "company_name",
            "recipient_email",
            "event_type",
            "priority",
            "channel",
            "status",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields


class AdminAuditLogEntrySerializer(serializers.ModelSerializer):
    # company is nullable on AuditLogEntry (not every action is
    # company-scoped — e.g. a user registering has no company yet), so
    # this needs a `default` for the source-chain traversal to survive a
    # None company rather than raising.
    company_name = serializers.CharField(
        source="company.name", read_only=True, default=None, allow_null=True
    )
    actor_email = serializers.EmailField(source="actor.email", read_only=True, default=None)

    class Meta:
        model = AuditLogEntry
        fields = [
            "id",
            "company_id",
            "company_name",
            "actor_email",
            "entity_type",
            "entity_id",
            "action",
            "old_value",
            "new_value",
            "source",
            "created_at",
        ]
        read_only_fields = fields
