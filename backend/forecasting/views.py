from decimal import Decimal, InvalidOperation

from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAuthenticatedReadOnlyOrCompanyAdmin
from .services import (
    generate_moving_average_forecast,
    generate_weighted_moving_average_forecast,
    get_forecast_vs_actual,
    get_forecast_vs_target,
)


class DailySalesForecastView(APIView):
    permission_classes = [IsAuthenticatedReadOnlyOrCompanyAdmin]

    def get(self, request):
        days = int(request.GET.get("days", 7))
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")

        if method == "moving_average":
            data = generate_moving_average_forecast(days=days, window=window)
        else:
            data = generate_weighted_moving_average_forecast(days=days, window=window)

        return Response(data)


class ForecastVsActualView(APIView):
    permission_classes = [IsAuthenticatedReadOnlyOrCompanyAdmin]

    def get(self, request):
        compare_days = int(request.GET.get("compare_days", 30))
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")

        data = get_forecast_vs_actual(
            compare_days=compare_days,
            window=window,
            method=method,
        )
        return Response(data)


class ForecastVsTargetView(APIView):
    permission_classes = [IsAuthenticatedReadOnlyOrCompanyAdmin]

    def get(self, request):
        target_amount_raw = request.GET.get("target_amount")
        if not target_amount_raw:
            return Response(
                {"detail": "target_amount query parameter is required."},
                status=400,
            )

        try:
            target_amount = Decimal(target_amount_raw)
        except (InvalidOperation, TypeError):
            return Response(
                {"detail": "target_amount must be a valid number."},
                status=400,
            )

        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")

        data = get_forecast_vs_target(
            target_amount=target_amount,
            window=window,
            method=method,
        )
        return Response(data)