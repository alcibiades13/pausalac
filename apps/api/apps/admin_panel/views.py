"""
System Admin views (master prompt §67). Every list here is deliberately
cross-tenant (`Model.objects.all()`, never `.for_company(...)`) — the one
place in the codebase where bypassing tenant scoping is correct, not a
bug. Read access is IsAdminUser (is_staff); state-changing actions are
IsSuperUser — see permissions.py for why.
"""

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.audit.models import AuditLogEntry
from apps.audit.services import AuditService
from apps.companies.models import Company, Membership
from apps.companies.serializers import CompanySerializer, MembershipSerializer
from apps.documents.models import Document
from apps.invoices.models import Invoice
from apps.limits.models import RegulatoryRule
from apps.notifications.models import Notification
from apps.subscriptions.models import Plan, Subscription
from apps.taxes.models import TaxObligation

from .serializers import (
    AdminAuditLogEntrySerializer,
    AdminDocumentSerializer,
    AdminInvoiceSerializer,
    AdminNotificationSerializer,
    AdminPlanSerializer,
    AdminRegulatoryRuleSerializer,
    AdminSubscriptionSerializer,
    AdminTaxObligationSerializer,
    AdminUserSerializer,
)


class AdminListView(generics.ListAPIView):
    """Shared base for every read-only admin list — is_staff is enough to
    browse, matching §67's "admin must support X" list. Write access
    (where it exists at all) is gated separately, per view, at
    IsSuperUser."""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class AdminUserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by("-date_joined")
    search_fields = ["email", "first_name", "last_name"]
    filterset_fields = ["is_active", "is_staff"]
    ordering_fields = ["date_joined", "email"]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ("deactivate", "reactivate"):
            from .permissions import IsSuperUser

            return [permissions.IsAuthenticated(), IsSuperUser()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        AuditService.log(
            actor=request.user,
            entity_type="user",
            entity_id=user.id,
            action="admin_deactivated",
        )
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"])
    def reactivate(self, request, pk=None, *args, **kwargs):
        """The self-service side (apps.accounts.DeactivateAccountView) has
        no reactivate counterpart on purpose (docs/data-retention.md:
        "needs an operator action") — this is that operator action."""
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        AuditService.log(
            actor=request.user,
            entity_type="user",
            entity_id=user.id,
            action="admin_reactivated",
        )
        return Response(self.get_serializer(user).data)


class AdminCompanyListView(AdminListView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by("name")
    search_fields = ["name", "legal_name", "pib"]
    filterset_fields = ["is_active", "country"]
    ordering_fields = ["name", "created_at"]


class AdminCompanyMembersView(APIView):
    """Not a ViewSet @action — AdminCompanyListView is a plain
    ListAPIView (no router involved), so this is its own view + explicit
    URL (urls.py) instead."""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk, *args, **kwargs):
        memberships = Membership.objects.filter(company_id=pk).select_related("user")
        return Response(MembershipSerializer(memberships, many=True).data)


class AdminSubscriptionListView(AdminListView):
    serializer_class = AdminSubscriptionSerializer
    queryset = Subscription.objects.select_related("company", "plan").order_by("-created_at")
    filterset_fields = ["status", "plan"]
    ordering_fields = ["created_at", "trial_ends_at"]


class AdminPlanViewSet(viewsets.ModelViewSet):
    """Full CRUD, unlike every other admin view here — Plan is the one
    entity (besides RegulatoryRule) genuinely edited day-to-day without a
    deploy (master prompt §50)."""

    serializer_class = AdminPlanSerializer
    queryset = Plan.objects.all().order_by("price")
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        from .permissions import IsSuperUser

        return [permissions.IsAuthenticated(), IsSuperUser()]

    def perform_create(self, serializer):
        plan = serializer.save()
        AuditService.log(
            actor=self.request.user,
            entity_type="plan",
            entity_id=plan.id,
            action="admin_created",
            new_value=AdminPlanSerializer(plan).data,
        )

    def perform_update(self, serializer):
        old_value = AdminPlanSerializer(serializer.instance).data
        plan = serializer.save()
        AuditService.log(
            actor=self.request.user,
            entity_type="plan",
            entity_id=plan.id,
            action="admin_updated",
            old_value=old_value,
            new_value=AdminPlanSerializer(plan).data,
        )


class AdminInvoiceListView(AdminListView):
    """Read-only — support/debugging visibility only, never editing
    another company's financial records from here (master prompt §96's
    refund/correction concept is explicitly out of scope everywhere)."""

    serializer_class = AdminInvoiceSerializer
    queryset = Invoice.objects.select_related("company", "client").order_by("-created_at")
    search_fields = ["invoice_number"]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "due_date"]


class AdminDocumentListView(AdminListView):
    serializer_class = AdminDocumentSerializer
    queryset = Document.objects.select_related("company", "uploaded_by").order_by("-created_at")
    search_fields = ["title", "original_filename"]
    filterset_fields = ["category"]
    ordering_fields = ["created_at"]


class AdminTaxObligationListView(AdminListView):
    serializer_class = AdminTaxObligationSerializer
    queryset = TaxObligation.objects.select_related("company").order_by("-period_start")
    filterset_fields = ["status"]
    ordering_fields = ["period_start", "due_date"]


class AdminRegulatoryRuleViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """List + create only — a new rule version is always a new row
    (matches the model's own "versioned, never edited" design, same as
    every other seed/reference table in this codebase); `approve` flips
    an existing row's approval_status instead."""

    serializer_class = AdminRegulatoryRuleSerializer
    queryset = RegulatoryRule.objects.all()
    filterset_fields = ["identifier", "approval_status"]
    ordering_fields = ["identifier", "effective_from", "version", "created_at"]

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        from .permissions import IsSuperUser

        return [permissions.IsAuthenticated(), IsSuperUser()]

    def perform_create(self, serializer):
        rule = serializer.save()
        AuditService.log(
            actor=self.request.user,
            entity_type="regulatory_rule",
            entity_id=rule.id,
            action="admin_created",
            new_value=AdminRegulatoryRuleSerializer(rule).data,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None, *args, **kwargs):
        rule = self.get_object()
        old_status = rule.approval_status
        rule.approval_status = RegulatoryRule.ApprovalStatus.CONFIRMED
        rule.save(update_fields=["approval_status"])
        AuditService.log(
            actor=request.user,
            entity_type="regulatory_rule",
            entity_id=rule.id,
            action="admin_approved",
            old_value={"approval_status": old_status},
            new_value={"approval_status": rule.approval_status},
        )
        return Response(self.get_serializer(rule).data)


class AdminNotificationListView(AdminListView):
    serializer_class = AdminNotificationSerializer
    queryset = Notification.objects.select_related("company", "recipient").order_by("-created_at")
    filterset_fields = ["priority", "channel", "status"]
    ordering_fields = ["created_at"]


class AdminAuditLogListView(AdminListView):
    serializer_class = AdminAuditLogEntrySerializer
    queryset = AuditLogEntry.objects.select_related("company", "actor").order_by("-created_at")
    filterset_fields = ["entity_type", "action", "source"]
    search_fields = ["entity_type", "entity_id", "action"]
    ordering_fields = ["created_at"]


class AdminIntegrationsStatusView(APIView):
    """A real status page, not a fake one — apps.integrations is still an
    empty placeholder (no SEF/NBS/fiscalization provider is chosen), so
    there's nothing to *manage* yet; this surfaces the real, already-
    checkable configuration state of Phase 6a's seams instead."""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        from config.health import _check_storage

        return Response(
            {
                "sentry": {"configured": bool(settings.SENTRY_DSN)},
                "storage": {"configured": _check_storage()},
                "email": {"configured": bool(settings.EMAIL_HOST)},
                "sef": {"configured": False, "note": "No provider chosen yet (§39)."},
                "checked_at": timezone.now().isoformat(),
            }
        )
