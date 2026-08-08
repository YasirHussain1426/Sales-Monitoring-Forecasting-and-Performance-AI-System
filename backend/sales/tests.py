from datetime import timedelta
from decimal import Decimal
from tkinter import Place

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Customer, Product, Region, SalesPerson, SalesTransaction


class SalesDashboardAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="salesuser1",
            email="sales1@example.com",
            password="testpass123",
        )
        self.user_two = user_model.objects.create_user(
            username="salesuser2",
            email="sales2@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=self.user)

        self.region_north = Region.objects.create(name="North", code="NORTH")
        self.region_south = Region.objects.create(name="South", code="SOUTH")

        self.product_a = Product.objects.create(
            name="Product A",
            sku="SKU-A",
            category="Category A",
            unit_price=Decimal("100.00"),
        )
        self.product_b = Product.objects.create(
            name="Product B",
            sku="SKU-B",
            category="Category B",
            unit_price=Decimal("200.00"),
        )

        self.customer_one = Customer.objects.create(
            name="Customer One",
            email="customer1@example.com",
            phone="1111111111",
            city="City A",
            region=self.region_north,
        )
        self.customer_two = Customer.objects.create(
            name="Customer Two",
            email="customer2@example.com",
            phone="2222222222",
            city="City B",
            region=self.region_south,
        )

        self.salesperson_north = SalesPerson.objects.create(
            user=self.user,
            employee_code="EMP-NORTH",
            region=self.region_north,
        )
        self.salesperson_south = SalesPerson.objects.create(
            user=self.user_two,
            employee_code="EMP-SOUTH",
            region=self.region_south,
        )

    def _create_transaction(
        self,
        *,
        transaction_date,
        customer,
        product,
        salesperson,
        quantity,
        unit_price,
        discount_amount=Decimal("0.00"),
    ):
        total_amount = (Decimal(str(quantity)) * unit_price) - discount_amount

        return SalesTransaction.objects.create(
            transaction_date=transaction_date,
            customer=customer,
            product=product,
            salesperson=salesperson,
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=discount_amount,
            total_amount=total_amount,
            notes="test transaction",
        )

    def test_dashboard_summary_returns_expected_metrics(self):
        today = timezone.localdate()

        self._create_transaction(
            transaction_date=today - timedelta(days=2),
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today - timedelta(days=1),
            customer=self.customer_one,
            product=self.product_b,
            salesperson=self.salesperson_north,
            quantity=2,
            unit_price=Decimal("200.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_two,
            product=self.product_a,
            salesperson=self.salesperson_south,
            quantity=3,
            unit_price=Decimal("100.00"),
        )

        response = self.client.get(
            reverse("sales-dashboard-summary"),
            {
                "start_date": (today - timedelta(days=2)).isoformat(),
                "end_date": today.isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["total_revenue"]), 800.0)
        self.assertEqual(response.data["total_transactions"], 3)
        self.assertEqual(response.data["total_quantity"], 6)
        self.assertAlmostEqual(float(response.data["average_order_value"]), 266.67, places=2)

    def test_dashboard_trends_groups_sales_by_day(self):
        today = timezone.localdate()

        self._create_transaction(
            transaction_date=today - timedelta(days=1),
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today - timedelta(days=1),
            customer=self.customer_two,
            product=self.product_b,
            salesperson=self.salesperson_south,
            quantity=1,
            unit_price=Decimal("200.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=2,
            unit_price=Decimal("100.00"),
        )

        response = self.client.get(
            reverse("sales-dashboard-trends"),
            {
                "start_date": (today - timedelta(days=1)).isoformat(),
                "end_date": today.isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        first_day = response.data[0]
        second_day = response.data[1]

        self.assertEqual(str(first_day["day"]), (today - timedelta(days=1)).isoformat())
        self.assertEqual(float(first_day["total_sales"]), 300.0)

        self.assertEqual(str(second_day["day"]), today.isoformat())
        self.assertEqual(float(second_day["total_sales"]), 200.0)

    def test_sales_by_region_uses_salesperson_region(self):
        today = timezone.localdate()

        self._create_transaction(
            transaction_date=today,
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_two,
            product=self.product_b,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("200.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_two,
            product=self.product_b,
            salesperson=self.salesperson_south,
            quantity=1,
            unit_price=Decimal("200.00"),
        )

        response = self.client.get(reverse("sales-by-region"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertEqual(response.data[0]["region"], "North")
        self.assertEqual(float(response.data[0]["total_sales"]), 300.0)

        self.assertEqual(response.data[1]["region"], "South")
        self.assertEqual(float(response.data[1]["total_sales"]), 200.0)

    def test_top_products_returns_sorted_products(self):
        today = timezone.localdate()

        self._create_transaction(
            transaction_date=today,
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_two,
            product=self.product_b,
            salesperson=self.salesperson_south,
            quantity=2,
            unit_price=Decimal("200.00"),
        )

        response = self.client.get(reverse("top-products"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

        self.assertEqual(response.data[0]["product_name"], "Product B")
        self.assertEqual(response.data[0]["sku"], "SKU-B")
        self.assertEqual(float(response.data[0]["total_sales"]), 400.0)

    def test_transactions_endpoint_filters_by_region_and_product(self):
        today = timezone.localdate()

        matching_transaction = self._create_transaction(
            transaction_date=today,
            customer=self.customer_one,
            product=self.product_a,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_two,
            product=self.product_a,
            salesperson=self.salesperson_south,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self._create_transaction(
            transaction_date=today,
            customer=self.customer_one,
            product=self.product_b,
            salesperson=self.salesperson_north,
            quantity=1,
            unit_price=Decimal("200.00"),
        )

        response = self.client.get(
            reverse("transactions-list"),
            {
                "region": self.region_north.id,
                "product": self.product_a.id,
                "start_date": today.isoformat(),
                "end_date": today.isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], matching_transaction.id)
        self.assertEqual(response.data["results"][0]["region_name"], "North")
        self.assertEqual(response.data["results"][0]["product_name"], "Product A")