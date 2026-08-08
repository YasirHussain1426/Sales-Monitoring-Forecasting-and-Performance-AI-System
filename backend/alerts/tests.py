from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import Alert
from sales.models import Customer, Product, Region, SalesPerson, SalesTransaction
from targets.models import SalesTarget


class AlertsAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="alertuser",
            email="alert@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        self.region = Region.objects.create(name="North", code="NORTH")
        self.product = Product.objects.create(
            name="Product A",
            sku="SKU-001",
            category="Category A",
            unit_price=Decimal("100.00"),
        )
        self.customer = Customer.objects.create(
            name="Customer One",
            email="customer@example.com",
            phone="1234567890",
            city="City A",
            region=self.region,
        )
        self.salesperson = SalesPerson.objects.create(
            user=self.user,
            employee_code="EMP-001",
            region=self.region,
        )

    def _create_constant_sales_history(self, total_days=10, amount=Decimal("100.00")):
        today = timezone.localdate()
        start_date = today - timedelta(days=total_days - 1)

        for offset in range(total_days):
            transaction_date = start_date + timedelta(days=offset)
            SalesTransaction.objects.create(
                transaction_date=transaction_date,
                customer=self.customer,
                product=self.product,
                salesperson=self.salesperson,
                quantity=1,
                unit_price=amount,
                discount_amount=Decimal("0.00"),
                total_amount=amount,
                notes="test transaction",
            )

        return start_date, today

    def test_run_alert_rules_creates_target_shortfall_alert(self):
        start_date, today = self._create_constant_sales_history(
            total_days=7,
            amount=Decimal("100.00"),
        )

        SalesTarget.objects.create(
            target_type="overall",
            period_start=start_date,
            period_end=today + timedelta(days=3),
            target_amount=Decimal("1500.00"),
        )

        url = reverse("run-alert-rules")
        response = self.client.post(
            url,
            {
                "method": "weighted",
                "window": 7,
                "compare_days": 30,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

        alerts = Alert.objects.filter(alert_type="forecast_target_shortfall")
        self.assertEqual(alerts.count(), 1)

        alert = alerts.first()
        self.assertEqual(alert.status, "open")
        self.assertEqual(alert.scope_type, "overall")
        self.assertEqual(alert.severity, "high")
        self.assertIn("Projected attainment", alert.message)

    def test_run_alert_rules_creates_high_error_alert(self):
        today = timezone.localdate()
        start_date = today - timedelta(days=9)

        values = [
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("400.00"),
            Decimal("400.00"),
            Decimal("400.00"),
        ]

        for offset, amount in enumerate(values):
            transaction_date = start_date + timedelta(days=offset)
            SalesTransaction.objects.create(
                transaction_date=transaction_date,
                customer=self.customer,
                product=self.product,
                salesperson=self.salesperson,
                quantity=1,
                unit_price=amount,
                discount_amount=Decimal("0.00"),
                total_amount=amount,
                notes="test transaction",
            )

        SalesTarget.objects.create(
            target_type="overall",
            period_start=start_date,
            period_end=today + timedelta(days=2),
            target_amount=Decimal("5000.00"),
        )

        url = reverse("run-alert-rules")
        response = self.client.post(
            url,
            {
                "method": "moving_average",
                "window": 7,
                "compare_days": 30,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        alerts = Alert.objects.filter(alert_type="forecast_error_high")
        self.assertEqual(alerts.count(), 1)

        alert = alerts.first()
        self.assertEqual(alert.status, "open")
        self.assertEqual(alert.scope_type, "overall")
        self.assertIn("Forecast WAPE", alert.message)
        self.assertIn("wape", alert.metadata)

    def test_resolve_alert_marks_status_resolved(self):
        alert = Alert.objects.create(
            alert_type="forecast_target_shortfall",
            severity="high",
            status="open",
            title="Overall target likely to miss",
            message="Projected attainment is 82%.",
            scope_type="overall",
            triggered_for_date=timezone.localdate(),
            metadata={"projected_total": 820.0},
        )

        url = reverse("resolve-alert", kwargs={"alert_id": alert.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertEqual(alert.status, "resolved")
        self.assertEqual(response.data["status"], "resolved")

    def test_alert_list_filters_open_alerts(self):
        today = timezone.localdate()

        Alert.objects.create(
            alert_type="forecast_target_shortfall",
            severity="high",
            status="open",
            title="Open alert",
            message="Open message",
            scope_type="overall",
            triggered_for_date=today,
            metadata={},
        )
        Alert.objects.create(
            alert_type="forecast_error_high",
            severity="medium",
            status="resolved",
            title="Resolved alert",
            message="Resolved message",
            scope_type="overall",
            triggered_for_date=today,
            metadata={},
        )

        url = reverse("alert-list")
        response = self.client.get(url, {"status": "open"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "open")
        self.assertEqual(response.data[0]["title"], "Open alert")