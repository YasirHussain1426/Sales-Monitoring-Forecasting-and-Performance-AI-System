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
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")
        scope_type = request.GET.get("scope_type", "overall")

        region_id_raw = request.GET.get("region_id")
        product_id_raw = request.GET.get("product_id")
        salesperson_id_raw = request.GET.get("salesperson_id")

        region_id = int(region_id_raw) if region_id_raw else None
        product_id = int(product_id_raw) if product_id_raw else None
        salesperson_id = int(salesperson_id_raw) if salesperson_id_raw else None
        try:
            data = get_forecast_vs_target(
                window=window,
                method=method,
                scope_type=scope_type,
                region_id=region_id,
                product_id=product_id,
                salesperson_id=salesperson_id,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=400,
            )

        if "detail" in data and "No active" in data["detail"]:
            return Response(data, status=404)

        return Response(data)