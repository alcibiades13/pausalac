"""
System Admin gating (master prompt §30/§67). No new role/table — reuses
Django's own is_staff/is_superuser, exactly as apps/accounts/models.py's
User docstring has said since Phase 1b: "is_staff/is_superuser only gate
the Django admin (System Admin, §67)." Read access is is_staff (DRF's
stock IsAdminUser); write access is is_superuser — a genuinely stronger,
pre-existing Django concept, and the concrete answer to §67's "must not
expose dangerous operations without appropriate permissions."
"""

from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_superuser)
