from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.permissions import HasActiveCompany, HasCompanyPermission

from .models import Plan
from .serializers import ActivatePlanSerializer, PlanSerializer, SubscriptionSerializer
from .services import SubscriptionService


class PlanListView(generics.ListAPIView):
    """Not company-scoped — plans are the same for everyone, this is
    just the catalog. IsAuthenticated only, no X-Company-Id needed."""

    serializer_class = PlanSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)


class SubscriptionView(APIView):
    """Current company's subscription — broadly readable (any active
    member), same reasoning as most status/read data in this app; only
    activate/cancel are OWNER-gated below."""

    permission_classes = [permissions.IsAuthenticated, HasActiveCompany]

    def get(self, request, *args, **kwargs):
        subscription = SubscriptionService.get_or_create_trial(request.company)
        return Response(SubscriptionSerializer(subscription).data)


class ActivatePlanView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("manage_subscriptions")]

    def post(self, request, *args, **kwargs):
        payload = ActivatePlanSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        subscription = SubscriptionService.get_or_create_trial(request.company)
        subscription = SubscriptionService.activate_plan(
            subscription, payload.validated_data["plan"], actor=request.user
        )
        return Response(SubscriptionSerializer(subscription).data)


class CancelSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("manage_subscriptions")]

    def post(self, request, *args, **kwargs):
        subscription = SubscriptionService.get_or_create_trial(request.company)
        subscription = SubscriptionService.cancel(subscription, actor=request.user)
        return Response(SubscriptionSerializer(subscription).data)
