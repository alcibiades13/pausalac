from datetime import date
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


class LimitHistoryView(APIView):
    """Monthly history + projection for `LimitProgressChart` (blueprint
    §6.5) — a separate endpoint from `LimitsView` on purpose, so the
    dashboard/limits-summary fetch (which calls `compute_all` from
    several places) doesn't pay for the extra monthly-grouping query on
    every load, only the Limits detail page that actually renders the
    chart."""

    permission_classes = [permissions.IsAuthenticated, HasCompanyPermission("view_financial_data")]

    def get(self, request, *args, **kwargs):
        raw_year = request.query_params.get("year")
        try:
            year = int(raw_year) if raw_year else date.today().year
        except ValueError:
            raise ValidationError({"year": ["Unesite ispravnu godinu."]}) from None
        return Response(LimitsService.compute_pausal_limit_history(request.company, year))


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
