from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    generate_moving_average_forecast,
    generate_weighted_moving_average_forecast,
    get_forecast_vs_actual,
    get_forecast_vs_target,
)


class DailySalesForecastView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")

        data = get_forecast_vs_target(
            window=window,
            method=method,
        )

        status_code = 404 if "detail" in data else 200
        return Response(data, status=status_code)