from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from sales.models import Customer, Product, Region, SalesPerson, SalesTransaction
from targets.models import SalesTarget


class ForecastingAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="forecastuser",
            email="forecast@example.com",
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

    def test_forecast_vs_actual_returns_zero_error_for_constant_sales(self):
        self._create_constant_sales_history(total_days=10, amount=Decimal("100.00"))

        url = reverse("forecast-vs-actual")
        response = self.client.get(
            url,
            {
                "compare_days": 30,
                "window": 7,
                "method": "weighted",
                "scope_type": "overall",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertIn("series", response.data)

        summary = response.data["summary"]
        self.assertEqual(summary["compared_points"], 3)
        self.assertEqual(summary["wape"], 0.0)
        self.assertEqual(summary["bias"], "neutral")
        self.assertEqual(summary["scope_type"], "overall")

        self.assertEqual(len(response.data["series"]), 3)
        for item in response.data["series"]:
            self.assertEqual(item["predicted_value"], 100.0)
            self.assertEqual(item["actual_value"], 100.0)
            self.assertEqual(item["error"], 0.0)

    def test_forecast_vs_target_returns_expected_overall_projection(self):
        start_date, today = self._create_constant_sales_history(
            total_days=7,
            amount=Decimal("100.00"),
        )
        period_end = today + timedelta(days=3)

        SalesTarget.objects.create(
            target_type="overall",
            period_start=start_date,
            period_end=period_end,
            target_amount=Decimal("1200.00"),
        )

        url = reverse("forecast-vs-target")
        response = self.client.get(
            url,
            {
                "window": 7,
                "method": "weighted",
                "scope_type": "overall",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["actual_to_date"], 700.0)
        self.assertEqual(response.data["forecast_remaining"], 300.0)
        self.assertEqual(response.data["projected_total"], 1000.0)
        self.assertEqual(response.data["target_amount"], 1200.0)
        self.assertEqual(response.data["variance_amount"], -200.0)
        self.assertAlmostEqual(response.data["attainment_pct"], 83.33, places=2)
        self.assertEqual(response.data["risk_status"], "likely_miss")
        self.assertEqual(response.data["scope_type"], "overall")
        self.assertEqual(response.data["target_type"], "overall")

    def test_forecast_vs_target_supports_region_scope(self):
        start_date, today = self._create_constant_sales_history(
            total_days=7,
            amount=Decimal("100.00"),
        )
        period_end = today + timedelta(days=2)

        SalesTarget.objects.create(
            target_type="region",
            region=self.region,
            period_start=start_date,
            period_end=period_end,
            target_amount=Decimal("1000.00"),
        )

        url = reverse("forecast-vs-target")
        response = self.client.get(
            url,
            {
                "window": 7,
                "method": "weighted",
                "scope_type": "region",
                "region_id": self.region.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["scope_type"], "region")
        self.assertEqual(response.data["region_id"], self.region.id)
        self.assertEqual(response.data["target_type"], "region")
        self.assertEqual(response.data["actual_to_date"], 700.0)
        self.assertEqual(response.data["forecast_remaining"], 200.0)
        self.assertEqual(response.data["projected_total"], 900.0)
        self.assertEqual(response.data["target_amount"], 1000.0)
        self.assertEqual(response.data["risk_status"], "likely_miss")