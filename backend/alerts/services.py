from decimal import Decimal

from django.utils import timezone

from forecasting.services import get_forecast_vs_actual, get_forecast_vs_target
from targets.models import SalesTarget

from .models import Alert


def _scope_from_target(target):
    if target.target_type == "overall":
        return {
            "scope_type": "overall",
            "region_id": None,
            "product_id": None,
            "salesperson_id": None,
            "region": None,
            "product": None,
            "salesperson": None,
        }

    if target.target_type == "region":
        return {
            "scope_type": "region",
            "region_id": target.region_id,
            "product_id": None,
            "salesperson_id": None,
            "region": target.region,
            "product": None,
            "salesperson": None,
        }

    if target.target_type == "product":
        return {
            "scope_type": "product",
            "region_id": None,
            "product_id": target.product_id,
            "salesperson_id": None,
            "region": None,
            "product": target.product,
            "salesperson": None,
        }

    return {
        "scope_type": "salesperson",
        "region_id": None,
        "product_id": None,
        "salesperson_id": target.salesperson_id,
        "region": None,
        "product": None,
        "salesperson": target.salesperson,
    }


def _upsert_alert(
    *,
    alert_type,
    severity,
    title,
    message,
    triggered_for_date,
    scope_type,
    region=None,
    product=None,
    salesperson=None,
    target=None,
    metadata=None,
):
    alert = (
        Alert.objects.filter(
            alert_type=alert_type,
            triggered_for_date=triggered_for_date,
            scope_type=scope_type,
            region=region,
            product=product,
            salesperson=salesperson,
            status="open",
        )
        .order_by("-created_at")
        .first()
    )

    if alert:
        alert.severity = severity
        alert.title = title
        alert.message = message
        alert.target = target
        alert.metadata = metadata or {}
        alert.save(
            update_fields=[
                "severity",
                "title",
                "message",
                "target",
                "metadata",
                "updated_at",
            ]
        )
        return alert, False

    return Alert.objects.create(
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        triggered_for_date=triggered_for_date,
        scope_type=scope_type,
        region=region,
        product=product,
        salesperson=salesperson,
        target=target,
        metadata=metadata or {},
    ), True


def run_target_shortfall_alerts(method="weighted", window=7, threshold_pct=Decimal("95")):
    today = timezone.localdate()

    active_targets = SalesTarget.objects.filter(
        period_start__lte=today,
        period_end__gte=today,
    ).select_related("region", "product", "salesperson")

    created_count = 0
    updated_count = 0

    for target in active_targets:
        scope = _scope_from_target(target)

        payload = get_forecast_vs_target(
            method=method,
            window=window,
            scope_type=scope["scope_type"],
            region_id=scope["region_id"],
            product_id=scope["product_id"],
            salesperson_id=scope["salesperson_id"],
        )

        if "detail" in payload:
            continue

        attainment_pct = Decimal(str(payload["attainment_pct"]))
        if attainment_pct >= threshold_pct:
            continue

        severity = "high" if attainment_pct < Decimal("90") else "medium"

        alert, created = _upsert_alert(
            alert_type="forecast_target_shortfall",
            severity=severity,
            title=f"{scope['scope_type'].title()} target likely to miss",
            message=(
                f"Projected attainment is {payload['attainment_pct']}% "
                f"for the current target period."
            ),
            triggered_for_date=today,
            scope_type=scope["scope_type"],
            region=scope["region"],
            product=scope["product"],
            salesperson=scope["salesperson"],
            target=target,
            metadata={
                "projected_total": payload["projected_total"],
                "target_amount": payload["target_amount"],
                "variance_amount": payload["variance_amount"],
                "risk_status": payload["risk_status"],
                "forecast_method": payload["forecast_method"],
            },
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "rule": "forecast_target_shortfall",
        "created": created_count,
        "updated": updated_count,
    }


def run_high_error_alerts(method="weighted", window=7, compare_days=30, wape_threshold=Decimal("0.20")):
    today = timezone.localdate()

    active_targets = SalesTarget.objects.filter(
        period_start__lte=today,
        period_end__gte=today,
    ).select_related("region", "product", "salesperson")

    created_count = 0
    updated_count = 0

    for target in active_targets:
        scope = _scope_from_target(target)

        payload = get_forecast_vs_actual(
            compare_days=compare_days,
            window=window,
            method=method,
            scope_type=scope["scope_type"],
            region_id=scope["region_id"],
            product_id=scope["product_id"],
            salesperson_id=scope["salesperson_id"],
        )

        summary = payload.get("summary", {})
        compared_points = summary.get("compared_points", 0)
        wape = Decimal(str(summary.get("wape", 0)))

        if compared_points == 0 or wape < wape_threshold:
            continue

        severity = "high" if wape >= Decimal("0.35") else "medium"

        alert, created = _upsert_alert(
            alert_type="forecast_error_high",
            severity=severity,
            title=f"{scope['scope_type'].title()} forecast error is high",
            message=(
                f"Forecast WAPE is {summary.get('wape')} over "
                f"{summary.get('compared_points')} comparison points."
            ),
            triggered_for_date=today,
            scope_type=scope["scope_type"],
            region=scope["region"],
            product=scope["product"],
            salesperson=scope["salesperson"],
            target=target,
            metadata={
                "wape": summary.get("wape"),
                "bias": summary.get("bias"),
                "compared_points": summary.get("compared_points"),
                "forecast_method": summary.get("method"),
            },
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "rule": "forecast_error_high",
        "created": created_count,
        "updated": updated_count,
    }


def run_all_alert_rules(method="weighted", window=7, compare_days=30):
    shortfall_result = run_target_shortfall_alerts(
        method=method,
        window=window,
    )
    error_result = run_high_error_alerts(
        method=method,
        window=window,
        compare_days=compare_days,
    )

    return {
        "status": "ok",
        "results": [
            shortfall_result,
            error_result,
        ],
    }