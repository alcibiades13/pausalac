from rest_framework.routers import DefaultRouter

from .views import AccountingOrganizationViewSet, ClientConnectionViewSet

router = DefaultRouter()
router.register("organizations", AccountingOrganizationViewSet, basename="accounting-organization")
router.register("connections", ClientConnectionViewSet, basename="accounting-connection")

urlpatterns = router.urls
