from rest_framework.permissions import BasePermission

from apps.companies.permissions import resolve_company

from .services import SubscriptionService


class HasActiveSubscription(BasePermission):
    """
    Added alongside (never instead of) the existing RBAC permission on a
    gated action — see apps/invoices/views.py::InvoiceViewSet.get_permissions,
    the single place this is wired up this phase (master prompt §104:
    "backend must enforce" entitlements, proven end-to-end on one real
    action rather than swept across every domain at once).
    """

    def has_permission(self, request, view) -> bool:
        request.company = resolve_company(request)
        if request.company is None:
            return False
        return SubscriptionService.has_active_access(request.company)
