from django.db import transaction
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Company, Membership
from .permissions import IsCompanyOwner
from .serializers import CompanySerializer, MembershipSerializer


class IsCompanyMember(permissions.BasePermission):
    """Object-level: any active membership (any role) grants read access."""

    def has_object_permission(self, request, view, obj: Company) -> bool:
        if request.user.is_superuser:
            return True
        return Membership.objects.filter(
            user=request.user, company=obj, status=Membership.Status.ACTIVE
        ).exists()


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Companies the current user belongs to. Company creation provisions the
    requesting user as OWNER in the same transaction (master prompt: a
    company should never exist without an owning member).

    Update is restricted to OWNER; this endpoint intentionally does not use
    the X-Company-Id header scoping (apps.companies.permissions) — a
    company is addressed directly by its own id here, since a user may be
    choosing between several companies before any one of them is "active".
    """

    serializer_class = CompanySerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        return Company.objects.filter(
            memberships__user=user, memberships__status=Membership.Status.ACTIVE
        ).distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update"):
            return [permissions.IsAuthenticated(), IsCompanyOwner()]
        if self.action in ("retrieve", "members", "onboarding"):
            return [permissions.IsAuthenticated(), IsCompanyMember()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        with transaction.atomic():
            company = serializer.save()
            Membership.objects.create(
                user=self.request.user, company=company, role=Membership.Role.OWNER
            )

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None, *args, **kwargs):
        company = self.get_object()
        if not request.user.has_company_permission(company, "manage_users"):
            raise exceptions.PermissionDenied("Nemate dozvolu da vidite članove ove kompanije.")
        memberships = Membership.objects.filter(company=company).select_related("user")
        return Response(MembershipSerializer(memberships, many=True).data)

    @action(detail=True, methods=["get"])
    def onboarding(self, request, pk=None, *args, **kwargs):
        """
        Onboarding-completion widget data (master prompt §34): what's done,
        what's missing, as a percentage. Computed on read, never stored, so
        it can't drift from the records it's summarizing.

        Imports apps.clients.models.Client lazily: companies is a
        lower-level domain that clients depends on (Client FKs to Company),
        so reaching "up" into clients here is a deliberate, contained
        exception for this one cross-domain read, not a module-level
        coupling — see docs/decisions-log.md.
        """
        from apps.clients.models import Client

        company = self.get_object()

        completed = []
        missing = []

        if company.name and company.pib:
            completed.append("company")
        else:
            missing.append("company")

        if company.bank_account:
            completed.append("bank")
        else:
            missing.append("bank")

        if Client.objects.for_company(company).filter(is_active=True).exists():
            completed.append("client")
        else:
            missing.append("client")

        # Not built yet (SEF integration is Phase 4+, Documents is a later
        # Phase 2/3 domain) — honestly reported as missing rather than
        # silently omitted, matching §34's own example list.
        missing.extend(["sef", "tax_document"])

        total = len(completed) + len(missing)
        percentage = round(len(completed) / total * 100) if total else 0

        return Response({"completed": completed, "missing": missing, "percentage": percentage})
