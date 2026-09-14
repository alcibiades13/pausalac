from decimal import Decimal, InvalidOperation

from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.companies.permissions import HasCompanyPermission
from apps.limits.services import LimitsService


class LimitsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get(self, request, *args, **kwargs):
        return Response(LimitsService.compute_all(request.company))


class LimitsSimulateView(APIView):
    """What-if calculator (§19/§98) — read-only, same permission as
    LimitsView since it never writes anything, just recomputes."""

    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def post(self, request, *args, **kwargs):
        raw_amount = request.data.get("amount")
        try:
            amount = Decimal(str(raw_amount))
        except (InvalidOperation, TypeError):
            raise ValidationError({"amount": ["Unesite ispravan iznos."]}) from None
        if amount <= 0:
            raise ValidationError({"amount": ["Iznos mora biti veći od nule."]})
        return Response(LimitsService.simulate(request.company, amount))
