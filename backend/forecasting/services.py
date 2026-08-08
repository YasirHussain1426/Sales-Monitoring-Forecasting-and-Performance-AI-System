from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from sales.models import SalesTransaction
from targets.models import SalesTarget


SCOPE_CONFIG = {
    "overall": {
        "sales_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {},
        "target_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "target_type": "overall"
        },
    },
    "region": {
        "sales_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "salesperson__region_id": region_id
        },
        "target_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "target_type": "region",
            "region_id": region_id,
        },
    },
    "product": {
        "sales_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "product_id": product_id
        },
        "target_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "target_type": "product",
            "product_id": product_id,
        },
    },
    "salesperson": {
        "sales_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "salesperson_id": salesperson_id
        },
        "target_filter_builder": lambda region_id=None, product_id=None, salesperson_id=None: {
            "target_type": "salesperson",
            "salesperson_id": salesperson_id,
        },
    },
}


def _to_decimal(value) -> Decimal:
    return Decimal(str(value or 0))


def _to_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _month_bounds(anchor_date: date | None = None) -> tuple[date, date]:
    current = anchor_date or timezone.localdate()
    start = current.replace(day=1)
    end = current.replace(day=monthrange(current.year, current.month)[1])
    return start, end


def _validate_scope_inputs(scope_type, region_id=None, product_id=None, salesperson_id=None):
    if scope_type not in SCOPE_CONFIG:
        raise ValueError("scope_type must be one of: overall, region, product, salesperson")

    if scope_type == "region" and not region_id:
        raise ValueError("region_id is required when scope_type=region")
    if scope_type == "product" and not product_id:
        raise ValueError("product_id is required when scope_type=product")
    if scope_type == "salesperson" and not salesperson_id:
        raise ValueError("salesperson_id is required when scope_type=salesperson")


def _build_sales_filters(scope_type, region_id=None, product_id=None, salesperson_id=None):
    _validate_scope_inputs(scope_type, region_id, product_id, salesperson_id)
    return SCOPE_CONFIG[scope_type]["sales_filter_builder"](
        region_id=region_id,
        product_id=product_id,
        salesperson_id=salesperson_id,
    )


def _build_target_filters(scope_type, region_id=None, product_id=None, salesperson_id=None):
    _validate_scope_inputs(scope_type, region_id, product_id, salesperson_id)
    return SCOPE_CONFIG[scope_type]["target_filter_builder"](
        region_id=region_id,
        product_id=product_id,
        salesperson_id=salesperson_id,
    )


def _get_daily_sales_rows(
    date_from: date | None = None,
    date_to: date | None = None,
    sales_filters: dict | None = None,
):
    queryset = SalesTransaction.objects.all()

    if sales_filters:
        queryset = queryset.filter(**sales_filters)

    if date_from:
        queryset = queryset.filter(transaction_date__gte=date_from)
    if date_to:
        queryset = queryset.filter(transaction_date__lte=date_to)

    return (
        queryset.values("transaction_date")
        .annotate(total_sales=Sum("total_amount"))
        .order_by("transaction_date")
    )


def _get_decimal_history(
    date_from: date | None = None,
    date_to: date | None = None,
    sales_filters: dict | None = None,
):
    rows = _get_daily_sales_rows(
        date_from=date_from,
        date_to=date_to,
        sales_filters=sales_filters,
    )
    return [(row["transaction_date"], _to_decimal(row["total_sales"])) for row in rows]


def get_daily_sales_history(
    date_from: date | None = None,
    date_to: date | None = None,
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
):
    sales_filters = _build_sales_filters(scope_type, region_id, product_id, salesperson_id)
    history = _get_decimal_history(
        date_from=date_from,
        date_to=date_to,
        sales_filters=sales_filters,
    )
    return [{"date": day.isoformat(), "sales": _to_float(total_sales)} for day, total_sales in history]


def _simple_average(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")
    return sum(values) / Decimal(len(values))


def _weighted_average(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")

    weights = [Decimal(index) for index in range(1, len(values) + 1)]
    weighted_sum = sum(value * weight for value, weight in zip(values, weights))
    total_weight = sum(weights)
    return weighted_sum / total_weight


def _build_forecast_payload(
    history: list[tuple[date, Decimal]],
    days: int,
    average_value: Decimal,
    start_after: date | None = None,
):
    if not history:
        return {"history": [], "forecast": []}

    last_history_date = history[-1][0]
    base_date = max(last_history_date, start_after) if start_after else last_history_date

    forecast = []
    for step in range(1, days + 1):
        forecast_date = base_date + timedelta(days=step)
        forecast.append(
            {
                "date": forecast_date.isoformat(),
                "predicted_sales": _to_float(average_value),
            }
        )

    return {
        "history": [{"date": day.isoformat(), "sales": _to_float(total_sales)} for day, total_sales in history],
        "forecast": forecast,
    }


def generate_moving_average_forecast(
    days: int = 7,
    window: int = 7,
    start_after: date | None = None,
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
):
    sales_filters = _build_sales_filters(scope_type, region_id, product_id, salesperson_id)
    history = _get_decimal_history(sales_filters=sales_filters)
    if not history:
        return {"history": [], "forecast": []}

    recent_values = [sales for _, sales in history[-window:]]
    average_sales = _simple_average(recent_values)

    return _build_forecast_payload(
        history=history,
        days=days,
        average_value=average_sales,
        start_after=start_after,
    )


def generate_weighted_moving_average_forecast(
    days: int = 7,
    window: int = 7,
    start_after: date | None = None,
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
):
    sales_filters = _build_sales_filters(scope_type, region_id, product_id, salesperson_id)
    history = _get_decimal_history(sales_filters=sales_filters)
    if not history:
        return {"history": [], "forecast": []}

    recent_values = [sales for _, sales in history[-window:]]
    weighted_average = _weighted_average(recent_values)

    return _build_forecast_payload(
        history=history,
        days=days,
        average_value=weighted_average,
        start_after=start_after,
    )


def get_forecast_vs_actual(
    compare_days: int = 30,
    window: int = 7,
    method: str = "weighted",
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
):
    sales_filters = _build_sales_filters(scope_type, region_id, product_id, salesperson_id)
    history = _get_decimal_history(sales_filters=sales_filters)

    if len(history) <= window:
        return {
            "summary": {
                "wape": 0.0,
                "bias": "neutral",
                "compared_points": 0,
                "method": method,
                "scope_type": scope_type,
            },
            "series": [],
        }

    comparisons = []

    for index in range(window, len(history)):
        prior_values = [sales for _, sales in history[index - window:index]]
        predicted_value = _simple_average(prior_values) if method == "moving_average" else _weighted_average(prior_values)

        actual_date, actual_value = history[index]
        error = actual_value - predicted_value

        comparisons.append(
            {
                "date": actual_date,
                "predicted_value": predicted_value,
                "actual_value": actual_value,
                "error": error,
            }
        )

    comparisons = comparisons[-compare_days:]
    actual_sum = sum((item["actual_value"] for item in comparisons), Decimal("0"))
    abs_error_sum = sum((abs(item["error"]) for item in comparisons), Decimal("0"))
    signed_error_sum = sum((item["error"] for item in comparisons), Decimal("0"))
    wape = Decimal("0") if actual_sum == 0 else abs_error_sum / actual_sum

    if signed_error_sum > 0:
        bias = "under_forecasting"
    elif signed_error_sum < 0:
        bias = "over_forecasting"
    else:
        bias = "neutral"

    return {
        "summary": {
            "wape": float(round(wape, 4)),
            "bias": bias,
            "compared_points": len(comparisons),
            "method": method,
            "scope_type": scope_type,
        },
        "series": [
            {
                "date": item["date"].isoformat(),
                "predicted_value": _to_float(item["predicted_value"]),
                "actual_value": _to_float(item["actual_value"]),
                "error": _to_float(item["error"]),
            }
            for item in comparisons
        ],
    }


def _get_risk_status(attainment_pct: Decimal) -> str:
    if attainment_pct < Decimal("95"):
        return "likely_miss"
    if attainment_pct < Decimal("100"):
        return "at_risk"
    if attainment_pct < Decimal("105"):
        return "on_track"
    return "ahead"


def _get_active_target(
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
    anchor_date: date | None = None,
):
    current_date = anchor_date or timezone.localdate()
    target_filters = _build_target_filters(scope_type, region_id, product_id, salesperson_id)

    return (
        SalesTarget.objects.filter(
            period_start__lte=current_date,
            period_end__gte=current_date,
            **target_filters,
        )
        .order_by("-period_start")
        .first()
    )


def get_forecast_vs_target(
    window: int = 7,
    method: str = "weighted",
    scope_type: str = "overall",
    region_id: int | None = None,
    product_id: int | None = None,
    salesperson_id: int | None = None,
):
    today = timezone.localdate()
    target = _get_active_target(
        scope_type=scope_type,
        region_id=region_id,
        product_id=product_id,
        salesperson_id=salesperson_id,
        anchor_date=today,
    )

    if not target:
        return {"detail": f"No active {scope_type} sales target found for the current date."}

    sales_filters = _build_sales_filters(scope_type, region_id, product_id, salesperson_id)

    actual_end = min(today, target.period_end)
    actual_history = []

    if actual_end >= target.period_start:
        actual_history = _get_decimal_history(
            date_from=target.period_start,
            date_to=actual_end,
            sales_filters=sales_filters,
        )

    actual_to_date = sum((sales for _, sales in actual_history), Decimal("0"))
    forecast_remaining = Decimal("0")
    remaining_days = 0

    if today < target.period_end:
        remaining_days = (target.period_end - today).days

        if method == "moving_average":
            forecast_payload = generate_moving_average_forecast(
                days=remaining_days,
                window=window,
                start_after=today,
                scope_type=scope_type,
                region_id=region_id,
                product_id=product_id,
                salesperson_id=salesperson_id,
            )
        else:
            forecast_payload = generate_weighted_moving_average_forecast(
                days=remaining_days,
                window=window,
                start_after=today,
                scope_type=scope_type,
                region_id=region_id,
                product_id=product_id,
                salesperson_id=salesperson_id,
            )

        forecast_remaining = sum(
            (Decimal(str(item["predicted_sales"])) for item in forecast_payload["forecast"]),
            Decimal("0"),
        )

    target_amount_decimal = _to_decimal(target.target_amount)
    projected_total = actual_to_date + forecast_remaining
    variance_amount = projected_total - target_amount_decimal
    attainment_pct = Decimal("0") if target_amount_decimal == 0 else (projected_total / target_amount_decimal) * Decimal("100")

    return {
        "period_start": target.period_start.isoformat(),
        "period_end": target.period_end.isoformat(),
        "actual_to_date": _to_float(actual_to_date),
        "forecast_remaining": _to_float(forecast_remaining),
        "projected_total": _to_float(projected_total),
        "target_amount": _to_float(target_amount_decimal),
        "variance_amount": _to_float(variance_amount),
        "attainment_pct": _to_float(attainment_pct),
        "risk_status": _get_risk_status(attainment_pct),
        "forecast_method": method,
        "remaining_days": remaining_days,
        "target_id": target.id,
        "target_type": target.target_type,
        "scope_type": scope_type,
        "region_id": region_id,
        "product_id": product_id,
        "salesperson_id": salesperson_id,
    }