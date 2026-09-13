"""
Resolves the "active company" for a request from the `X-Company-Id` header
and validates it against the caller's active memberships (master prompt
§47 — tenant scope is never trusted from the frontend alone).

Implemented as DRF permission classes (rather than middleware or an
`initial()` override) so `request.company` is set as a side effect of
`check_permissions`, which DRF already runs before the view body executes
and before any other permission class needs to read it. See
docs/decisions-log.md for why this shape was chosen over the alternatives
sketched in the Phase 1b plan.
"""

from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from apps.companies.models import Membership


def resolve_company(request):
    """
    Idempotent within a request: resolves `X-Company-Id` against the
    caller's active memberships once, caches the result on the request.
    Raises a DRF exception on a missing/invalid/unauthorized header rather
    than silently falling back to "no company".
    """
    if hasattr(request, "_resolved_company"):
        return request._resolved_company

    if not request.user or not request.user.is_authenticated:
        request._resolved_company = None
        return None

    company_id = request.headers.get("X-Company-Id")
    if not company_id:
        raise exceptions.ValidationError({"company": "Nedostaje X-Company-Id header."})

    membership = (
        Membership.objects.filter(
            user=request.user, company_id=company_id, status=Membership.Status.ACTIVE
        )
        .select_related("company")
        .first()
    )
    if membership is None:
        raise exceptions.PermissionDenied("Nemate pristup ovoj kompaniji.")

    request._resolved_company = membership.company
    return membership.company


class HasActiveCompany(BasePermission):
    """Any active role on the resolved company is enough."""

    def has_permission(self, request, view) -> bool:
        request.company = resolve_company(request)
        return request.company is not None


def HasCompanyPermission(codename: str):
    """
    Factory: `permission_classes = [HasCompanyPermission("create_invoice")]`.
    Returns a class (not an instance) — DRF instantiates permission_classes
    entries itself, so a bare instance/closure wouldn't work here.
    """

    class _HasCompanyPermission(BasePermission):
        def has_permission(self, request, view) -> bool:
            request.company = resolve_company(request)
            if request.company is None:
                return False
            return request.user.has_company_permission(request.company, codename)

    _HasCompanyPermission.__name__ = f"HasCompanyPermission_{codename}"
    return _HasCompanyPermission


class IsCompanyOwner(BasePermission):
    """Object-level check for actions only the OWNER role may perform."""

    def has_object_permission(self, request, view, obj) -> bool:
        # `obj` is a Company instance here.
        if request.user.is_superuser:
            return True
        return Membership.objects.filter(
            user=request.user,
            company=obj,
            role=Membership.Role.OWNER,
            status=Membership.Status.ACTIVE,
        ).exists()
