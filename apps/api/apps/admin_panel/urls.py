from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminAuditLogListView,
    AdminCompanyListView,
    AdminCompanyMembersView,
    AdminDocumentListView,
    AdminIntegrationsStatusView,
    AdminInvoiceListView,
    AdminNotificationListView,
    AdminPlanViewSet,
    AdminRegulatoryRuleViewSet,
    AdminSubscriptionListView,
    AdminTaxObligationListView,
    AdminUserViewSet,
)

router = DefaultRouter()
router.register("users", AdminUserViewSet, basename="admin-user")
router.register("plans", AdminPlanViewSet, basename="admin-plan")
router.register("rules", AdminRegulatoryRuleViewSet, basename="admin-rule")

urlpatterns = [
    path("companies/", AdminCompanyListView.as_view(), name="admin-company-list"),
    path(
        "companies/<int:pk>/members/",
        AdminCompanyMembersView.as_view(),
        name="admin-company-members",
    ),
    path("subscriptions/", AdminSubscriptionListView.as_view(), name="admin-subscription-list"),
    path("invoices/", AdminInvoiceListView.as_view(), name="admin-invoice-list"),
    path("documents/", AdminDocumentListView.as_view(), name="admin-document-list"),
    path(
        "tax-obligations/",
        AdminTaxObligationListView.as_view(),
        name="admin-tax-obligation-list",
    ),
    path("notifications/", AdminNotificationListView.as_view(), name="admin-notification-list"),
    path("audit-log/", AdminAuditLogListView.as_view(), name="admin-audit-log-list"),
    path("integrations/", AdminIntegrationsStatusView.as_view(), name="admin-integrations-status"),
    path("", include(router.urls)),
]
