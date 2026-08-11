from core.permissions import IsCompanyAdmin
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Alert
from .services import run_all_alert_rules


class AlertListView(APIView):
    permission_classes = [IsCompanyAdmin]

    def get(self, request):
        queryset = Alert.objects.select_related(
            "region",
            "product",
            "salesperson",
            "target",
        ).all()

        status_filter = request.GET.get("status")
        severity_filter = request.GET.get("severity")
        alert_type_filter = request.GET.get("alert_type")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        if alert_type_filter:
            queryset = queryset.filter(alert_type=alert_type_filter)

        data = [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "status": alert.status,
                "title": alert.title,
                "message": alert.message,
                "scope_type": alert.scope_type,
                "region": alert.region.name if alert.region else None,
                "product": alert.product.name if alert.product else None,
                "salesperson": alert.salesperson.employee_code if alert.salesperson else None,
                "triggered_for_date": alert.triggered_for_date,
                "metadata": alert.metadata,
                "created_at": alert.created_at,
            }
            for alert in queryset
        ]
        return Response(data)


class RunAlertRulesView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        method = request.data.get("method", "weighted")
        window = int(request.data.get("window", 7))
        compare_days = int(request.data.get("compare_days", 30))

        result = run_all_alert_rules(
            method=method,
            window=window,
            compare_days=compare_days,
        )
        return Response(result)


class ResolveAlertView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request, alert_id):
        alert = get_object_or_404(Alert, id=alert_id)
        alert.status = "resolved"
        alert.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "id": alert.id,
                "status": alert.status,
                "message": "Alert marked as resolved.",
            }
        )