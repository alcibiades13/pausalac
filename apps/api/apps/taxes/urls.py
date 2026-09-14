from rest_framework.routers import DefaultRouter

from .views import TaxObligationViewSet, TaxResolutionViewSet

router = DefaultRouter()
router.register("resolutions", TaxResolutionViewSet, basename="tax-resolution")
router.register("obligations", TaxObligationViewSet, basename="tax-obligation")

urlpatterns = router.urls
