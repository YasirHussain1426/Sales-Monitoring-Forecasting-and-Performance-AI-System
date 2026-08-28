from core.models import UserProfile
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Customer, Product, Region, SalesPerson, SalesTransaction

User = get_user_model()

class SalesDashboardAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="salesuser1",
            email="sales1@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(
        user=self.user,
        role=UserProfile.Role.ANALYST,
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
        
class SalesTransactionPermissionTests(APITestCase):
    def create_user_with_role(self, username, role):
        user = User.objects.create_user(
            username=username,
            password="Strong@123",
        )

        UserProfile.objects.create(
            user=user,
            role=role,
        )

        return user

    def test_analyst_can_read_transactions(self):
        user = self.create_user_with_role(
            "analyst",
            UserProfile.Role.ANALYST,
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            reverse("transactions-list")
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_analyst_cannot_create_transaction(self):
        user = self.create_user_with_role(
            "analyst",
            UserProfile.Role.ANALYST,
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("transactions-list"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_salesperson_can_create_transaction(self):
        user = self.create_user_with_role(
            "salesperson",
            UserProfile.Role.SALESPERSON,
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("transactions-list"),
            {},
            format="json",
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_sales_manager_can_create_transaction(self):
        user = self.create_user_with_role(
            "manager",
            UserProfile.Role.SALES_MANAGER,
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("transactions-list"),
            {},
            format="json",
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_create_transaction(self):
        user = self.create_user_with_role(
            "admin",
            UserProfile.Role.COMPANY_ADMIN,
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("transactions-list"),
            {},
            format="json",
        )

        self.assertNotEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_salesperson_cannot_see_another_salespersons_transactions(self):
        region = Region.objects.create(name="Test North", code="TEST-NORTH")

        owner_user = User.objects.create_user(
            username="owner",
            password="Strong@123",
        )
        UserProfile.objects.create(
            user=owner_user,
            role=UserProfile.Role.SALESPERSON,
        )
        owner_salesperson = SalesPerson.objects.create(
            user=owner_user,
            employee_code="EMP-OWNER",
            region=region,
        )

        other_user = User.objects.create_user(
            username="other",
            password="Strong@123",
        )
        UserProfile.objects.create(
            user=other_user,
            role=UserProfile.Role.SALESPERSON,
        )
        other_salesperson = SalesPerson.objects.create(
            user=other_user,
            employee_code="EMP-OTHER",
            region=region,
        )

        customer = Customer.objects.create(
            name="Test Customer",
            email="test@example.com",
            region=region,
        )

        product = Product.objects.create(
            name="Test Product",
            sku="TEST-SKU",
            category="Test",
            unit_price=Decimal("100.00"),
        )

        transaction = SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer,
            product=product,
            salesperson=other_salesperson,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
        )

        self.client.force_authenticate(user=owner_user)

        response = self.client.get(
            reverse("transactions-list")
        )

        returned_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(transaction.id, returned_ids)


    def test_sales_manager_cannot_see_other_region_transactions(self):
        north = Region.objects.create(
            name="Manager North",
            code="MANAGER-NORTH",
        )
        south = Region.objects.create(
            name="Manager South",
            code="MANAGER-SOUTH",
        )

        manager_user = User.objects.create_user(
            username="manager_scope",
            password="Strong@123",
        )
        UserProfile.objects.create(
            user=manager_user,
            role=UserProfile.Role.SALES_MANAGER,
        )
        manager_salesperson = SalesPerson.objects.create(
            user=manager_user,
            employee_code="EMP-MANAGER",
            region=north,
        )

        south_user = User.objects.create_user(
            username="south_sales",
            password="Strong@123",
        )
        UserProfile.objects.create(
            user=south_user,
            role=UserProfile.Role.SALESPERSON,
        )
        south_salesperson = SalesPerson.objects.create(
            user=south_user,
            employee_code="EMP-SOUTH",
            region=south,
        )

        customer = Customer.objects.create(
            name="South Customer",
            region=south,
        )

        product = Product.objects.create(
            name="South Product",
            sku="SOUTH-SKU",
            category="Test",
            unit_price=Decimal("100.00"),
        )

        transaction = SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer,
            product=product,
            salesperson=south_salesperson,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
        )

        self.client.force_authenticate(user=manager_user)

        response = self.client.get(
            reverse("transactions-list")
        )

        returned_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(transaction.id, returned_ids)


    def test_company_admin_can_see_all_transactions(self):
        north = Region.objects.create(
            name="Admin North",
            code="ADMIN-NORTH",
        )
        south = Region.objects.create(
            name="Admin South",
            code="ADMIN-SOUTH",
        )

        admin_user = User.objects.create_user(
            username="company_admin",
            password="Strong@123",
        )
        UserProfile.objects.create(
            user=admin_user,
            role=UserProfile.Role.COMPANY_ADMIN,
        )

        north_user = User.objects.create_user(
            username="north_sales",
            password="Strong@123",
        )
        north_salesperson = SalesPerson.objects.create(
            user=north_user,
            employee_code="EMP-ADMIN-NORTH",
            region=north,
        )

        south_user = User.objects.create_user(
            username="south_admin_test",
            password="Strong@123",
        )
        south_salesperson = SalesPerson.objects.create(
            user=south_user,
            employee_code="EMP-ADMIN-SOUTH",
            region=south,
        )

        customer_north = Customer.objects.create(
            name="North Customer",
            region=north,
        )
        customer_south = Customer.objects.create(
            name="South Customer",
            region=south,
        )

        product = Product.objects.create(
            name="Admin Product",
            sku="ADMIN-SKU",
            category="Test",
            unit_price=Decimal("100.00"),
        )

        north_transaction = SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer_north,
            product=product,
            salesperson=north_salesperson,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
        )

        south_transaction = SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer_south,
            product=product,
            salesperson=south_salesperson,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
        )

        self.client.force_authenticate(user=admin_user)

        response = self.client.get(
            reverse("transactions-list")
        )

        returned_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(north_transaction.id, returned_ids)
        self.assertIn(south_transaction.id, returned_ids)
        
    def test_salesperson_dashboard_summary_is_scoped_to_own_sales(self):
        region = Region.objects.create(
            name="Dashboard Region",
            code="DASH-REGION",
        )

        salesperson_user = User.objects.create_user(
            username="dashboard_salesperson",
            password="Strong@123",
        )

        UserProfile.objects.create(
            user=salesperson_user,
            role=UserProfile.Role.SALESPERSON,
        )

        salesperson = SalesPerson.objects.create(
            user=salesperson_user,
            employee_code="EMP-DASH-01",
            region=region,
        )

        other_user = User.objects.create_user(
            username="dashboard_other",
            password="Strong@123",
        )

        UserProfile.objects.create(
            user=other_user,
            role=UserProfile.Role.SALESPERSON,
        )

        other_salesperson = SalesPerson.objects.create(
            user=other_user,
            employee_code="EMP-DASH-02",
            region=region,
        )

        customer = Customer.objects.create(
            name="Dashboard Customer",
            region=region,
        )

        product = Product.objects.create(
            name="Dashboard Product",
            sku="DASH-SKU",
            category="Test",
            unit_price=Decimal("100.00"),
        )

        SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer,
            product=product,
            salesperson=salesperson,
            quantity=1,
            unit_price=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
        )

        SalesTransaction.objects.create(
            transaction_date=timezone.localdate(),
            customer=customer,
            product=product,
            salesperson=other_salesperson,
            quantity=1,
            unit_price=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("500.00"),
        )

        self.client.force_authenticate(user=salesperson_user)

        response = self.client.get(
            reverse("sales-dashboard-summary")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            float(response.data["total_revenue"]),
            100.0,
        )

        self.assertEqual(
            response.data["total_transactions"],
            1,
        )
        
