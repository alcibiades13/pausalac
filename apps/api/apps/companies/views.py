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
        if self.action in ("retrieve", "members"):
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
