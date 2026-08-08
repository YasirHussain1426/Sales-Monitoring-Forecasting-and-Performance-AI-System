from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    generate_moving_average_forecast,
    generate_weighted_moving_average_forecast,
    get_forecast_vs_actual,
    get_forecast_vs_target,
)


def _optional_int(value):
    if value in (None, "", "null"):
        return None
    return int(value)


class DailySalesForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.GET.get("days", 7))
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")
        scope_type = request.GET.get("scope_type", "overall")
        region_id = _optional_int(request.GET.get("region_id"))
        product_id = _optional_int(request.GET.get("product_id"))
        salesperson_id = _optional_int(request.GET.get("salesperson_id"))

        if method == "moving_average":
            data = generate_moving_average_forecast(
                days=days,
                window=window,
                scope_type=scope_type,
                region_id=region_id,
                product_id=product_id,
                salesperson_id=salesperson_id,
            )
        else:
            data = generate_weighted_moving_average_forecast(
                days=days,
                window=window,
                scope_type=scope_type,
                region_id=region_id,
                product_id=product_id,
                salesperson_id=salesperson_id,
            )

        return Response(data)


class ForecastVsActualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        compare_days = int(request.GET.get("compare_days", 30))
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")
        scope_type = request.GET.get("scope_type", "overall")
        region_id = _optional_int(request.GET.get("region_id"))
        product_id = _optional_int(request.GET.get("product_id"))
        salesperson_id = _optional_int(request.GET.get("salesperson_id"))

        data = get_forecast_vs_actual(
            compare_days=compare_days,
            window=window,
            method=method,
            scope_type=scope_type,
            region_id=region_id,
            product_id=product_id,
            salesperson_id=salesperson_id,
        )
        return Response(data)


class ForecastVsTargetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        window = int(request.GET.get("window", 7))
        method = request.GET.get("method", "weighted")
        scope_type = request.GET.get("scope_type", "overall")
        region_id = _optional_int(request.GET.get("region_id"))
        product_id = _optional_int(request.GET.get("product_id"))
        salesperson_id = _optional_int(request.GET.get("salesperson_id"))

        data = get_forecast_vs_target(
            window=window,
            method=method,
            scope_type=scope_type,
            region_id=region_id,
            product_id=product_id,
            salesperson_id=salesperson_id,
        )

        status_code = 404 if "detail" in data else 200
        return Response(data, status=status_code)