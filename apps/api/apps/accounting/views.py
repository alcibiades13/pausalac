from django.shortcuts import get_object_or_404
from rest_framework import exceptions, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.companies.permissions import HasActiveCompany, HasCompanyPermission

from .dashboard import compute_client_portfolio, summarize_portfolio
from .models import AccountingConnection, AccountingOrganization, AccountingOrganizationMembership
from .serializers import (
    AccountingConnectionCreateSerializer,
    AccountingOrganizationMembershipCreateSerializer,
    AccountingOrganizationMembershipSerializer,
    AccountingOrganizationSerializer,
    ClientConnectionSerializer,
    OrganizationConnectionSerializer,
)
from .services import AccountingService


class IsOrgMember(permissions.BasePermission):
    """Object-level: any active staff membership (any role) grants read access."""

    def has_object_permission(self, request, view, obj: AccountingOrganization) -> bool:
        if request.user.is_superuser:
            return True
        return obj.staff_memberships.filter(
            user=request.user, status=AccountingOrganizationMembership.Status.ACTIVE
        ).exists()


class IsOrgAdmin(permissions.BasePermission):
    """Object-level: only an active `admin`-role staff member may manage staff/connections."""

    def has_object_permission(self, request, view, obj: AccountingOrganization) -> bool:
        if request.user.is_superuser:
            return True
        return obj.staff_memberships.filter(
            user=request.user,
            status=AccountingOrganizationMembership.Status.ACTIVE,
            role=AccountingOrganizationMembership.Role.ADMIN,
        ).exists()


class AccountingOrganizationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Accounting organizations the current user staffs. Own-id addressed,
    like CompanyViewSet — a user may belong to more than one org, and this
    isn't scoped by X-Company-Id (it has nothing to do with a "current
    company"). No update/destroy mixin — an organization is never edited
    or deleted this phase, and (unlike CompanyViewSet, which blocks this
    via `http_method_names`) that can't be used to block just the base
    resource here: it would also block DELETE on the `remove_staff`
    sub-action below.
    """

    serializer_class = AccountingOrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AccountingOrganization.objects.all()
        return AccountingOrganization.objects.filter(
            staff_memberships__user=user,
            staff_memberships__status=AccountingOrganizationMembership.Status.ACTIVE,
        ).distinct()

    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated(), IsOrgMember()]
        if self.action == "staff" and self.request.method == "GET":
            return [permissions.IsAuthenticated(), IsOrgMember()]
        if self.action in ("staff", "remove_staff", "connections") and self.request.method != "GET":
            return [permissions.IsAuthenticated(), IsOrgAdmin()]
        if self.action in ("connections", "dashboard"):
            return [permissions.IsAuthenticated(), IsOrgMember()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["get", "post"])
    def staff(self, request, pk=None, *args, **kwargs):
        organization = self.get_object()
        if request.method == "POST":
            payload = AccountingOrganizationMembershipCreateSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            membership = AccountingService.add_staff(
                organization, actor=request.user, **payload.validated_data
            )
            return Response(
                AccountingOrganizationMembershipSerializer(membership).data, status=201
            )
        memberships = organization.staff_memberships.filter(
            status=AccountingOrganizationMembership.Status.ACTIVE
        ).select_related("user")
        return Response(AccountingOrganizationMembershipSerializer(memberships, many=True).data)

    @action(detail=True, methods=["delete"], url_path="staff/(?P<membership_id>[^/.]+)")
    def remove_staff(self, request, pk=None, membership_id=None, *args, **kwargs):
        organization = self.get_object()
        membership = get_object_or_404(
            AccountingOrganizationMembership, pk=membership_id, organization=organization
        )
        AccountingService.remove_staff(membership, actor=request.user)
        return Response(status=204)

    @action(detail=True, methods=["get", "post"])
    def connections(self, request, pk=None, *args, **kwargs):
        organization = self.get_object()
        if request.method == "POST":
            payload = AccountingConnectionCreateSerializer(data=request.data)
            payload.is_valid(raise_exception=True)
            connection = AccountingService.create_connection(
                organization, actor=request.user, **payload.validated_data
            )
            return Response(OrganizationConnectionSerializer(connection).data, status=201)
        connections = organization.connections.select_related("company").all()
        return Response(OrganizationConnectionSerializer(connections, many=True).data)

    # A small fixed set of sortable fields (§92: tables need sorting) —
    # not arbitrary-field ordering, which this computed-in-Python list
    # (not a queryset) has no generic infrastructure for.
    _ORDERING_KEYS = {
        "name": lambda row: row["company_name"].lower(),
        "-name": lambda row: row["company_name"].lower(),
        "revenue": lambda row: row["revenue_ytd"],
        "-revenue": lambda row: row["revenue_ytd"],
    }

    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None, *args, **kwargs):
        """
        Accountant client-portfolio view (master prompt §28/§29). Every
        figure is computed once for the whole portfolio in
        apps.accounting.dashboard.compute_client_portfolio — filtering/
        sorting/pagination below all operate on that already-computed
        list, not on a fresh per-row query.
        """
        organization = self.get_object()
        portfolio = compute_client_portfolio(organization)
        summary = summarize_portfolio(portfolio)

        status_filter = request.query_params.get("status")
        if status_filter:
            portfolio = [row for row in portfolio if row["status"] == status_filter]
        search = request.query_params.get("search")
        if search:
            needle = search.lower()
            portfolio = [row for row in portfolio if needle in row["company_name"].lower()]

        ordering = request.query_params.get("ordering", "name")
        key = self._ORDERING_KEYS.get(ordering, self._ORDERING_KEYS["name"])
        portfolio.sort(key=key, reverse=ordering.startswith("-"))

        page = self.paginate_queryset(portfolio)
        if page is not None:
            response = self.get_paginated_response(page)
            response.data["summary"] = summary
            return response
        return Response({"summary": summary, "results": portfolio})


class ClientConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Client-side "Moj računovođa" view — connections for the currently
    active company (X-Company-Id header), same tenant-scoping mechanism
    as every other domain.
    """

    serializer_class = ClientConnectionSerializer

    def get_permissions(self):
        if self.action in ("accept", "decline", "revoke"):
            return [permissions.IsAuthenticated(), HasCompanyPermission("manage_users")()]
        return [permissions.IsAuthenticated(), HasActiveCompany()]

    def get_queryset(self):
        return AccountingConnection.objects.for_company(self.request.company).select_related(
            "organization"
        )

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None, *args, **kwargs):
        connection = self.get_object()
        if connection.status != AccountingConnection.Status.PENDING:
            raise exceptions.ValidationError("Ova veza više nije na čekanju.")
        connection = AccountingService.accept_connection(connection, actor=request.user)
        return Response(self.get_serializer(connection).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None, *args, **kwargs):
        connection = self.get_object()
        if connection.status != AccountingConnection.Status.PENDING:
            raise exceptions.ValidationError("Ova veza više nije na čekanju.")
        connection = AccountingService.decline_connection(connection, actor=request.user)
        return Response(self.get_serializer(connection).data)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None, *args, **kwargs):
        connection = self.get_object()
        if connection.status != AccountingConnection.Status.ACTIVE:
            raise exceptions.ValidationError("Samo aktivna veza može da se opozove.")
        connection = AccountingService.revoke_connection(connection, actor=request.user)
        return Response(self.get_serializer(connection).data)
