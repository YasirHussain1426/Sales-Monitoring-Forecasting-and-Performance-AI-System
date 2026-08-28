import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import UserProfile
from sales.models import (
    Customer,
    Product,
    Region,
    SalesPerson,
    SalesTransaction,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed realistic demo sales data with RBAC users and regional sales data"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING("Seeding demo sales data...")
        )

        # ---------------------------------------------------------
        # 1. REGIONS
        # ---------------------------------------------------------
        regions_data = [
            {"name": "North", "code": "NORTH"},
            {"name": "South", "code": "SOUTH"},
            {"name": "East", "code": "EAST"},
            {"name": "West", "code": "WEST"},
        ]

        region_objects = []

        for region_data in regions_data:
            region, _ = Region.objects.get_or_create(
                code=region_data["code"],
                defaults={
                    "name": region_data["name"],
                },
            )

            # Keep existing region names correct if they already exist.
            if region.name != region_data["name"]:
                region.name = region_data["name"]
                region.save(update_fields=["name"])

            region_objects.append(region)

        # ---------------------------------------------------------
        # 2. PRODUCTS
        # ---------------------------------------------------------
        products_data = [
            {
                "name": "Laptop",
                "sku": "LP100",
                "category": "Electronics",
                "unit_price": Decimal("75000.00"),
            },
            {
                "name": "Mouse",
                "sku": "MS200",
                "category": "Accessories",
                "unit_price": Decimal("1200.00"),
            },
            {
                "name": "Keyboard",
                "sku": "KB300",
                "category": "Accessories",
                "unit_price": Decimal("2500.00"),
            },
            {
                "name": "Monitor",
                "sku": "MN400",
                "category": "Electronics",
                "unit_price": Decimal("18000.00"),
            },
            {
                "name": "Printer",
                "sku": "PR500",
                "category": "Office",
                "unit_price": Decimal("14000.00"),
            },
            {
                "name": "Desk Chair",
                "sku": "DC600",
                "category": "Furniture",
                "unit_price": Decimal("8500.00"),
            },
            {
                "name": "Tablet",
                "sku": "TB700",
                "category": "Electronics",
                "unit_price": Decimal("32000.00"),
            },
            {
                "name": "Webcam",
                "sku": "WC800",
                "category": "Accessories",
                "unit_price": Decimal("3500.00"),
            },
            {
                "name": "Headset",
                "sku": "HS900",
                "category": "Accessories",
                "unit_price": Decimal("4200.00"),
            },
            {
                "name": "Router",
                "sku": "RT1000",
                "category": "Networking",
                "unit_price": Decimal("6800.00"),
            },
        ]

        product_objects = []

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data["sku"],
                defaults={
                    "name": product_data["name"],
                    "category": product_data["category"],
                    "unit_price": product_data["unit_price"],
                    "is_active": True,
                },
            )

            # Keep seeded product values aligned.
            if not created:
                changed = False

                for field in (
                    "name",
                    "category",
                    "unit_price",
                    
                ):
                    new_value = product_data[field]

                    if getattr(product, field) != new_value:
                        setattr(product, field, new_value)
                        changed = True

                if changed:
                    product.save()

            product_objects.append(product)

        # ---------------------------------------------------------
        # 3. USERS / ROLES
        # ---------------------------------------------------------
        #
        # Public signup must NEVER create privileged users.
        # These are development/demo accounts created explicitly
        # by this management command.
        #
        demo_password = "Password123!"

        demo_accounts = []

        # Company admin
        admin_user = self._get_or_create_user(
            username="demo_admin",
            email="demo_admin@example.com",
            password=demo_password,
            role=UserProfile.Role.COMPANY_ADMIN,
        )

        demo_accounts.append(admin_user)

        # Company analyst
        analyst_user = self._get_or_create_user(
            username="demo_analyst",
            email="demo_analyst@example.com",
            password=demo_password,
            role=UserProfile.Role.ANALYST,
        )

        demo_accounts.append(analyst_user)

        # ---------------------------------------------------------
        # 4. REGIONAL MANAGERS + SALESPERSONS
        # ---------------------------------------------------------
        regional_salespeople = []
        manager_by_region = {}

        for region in region_objects:
            region_slug = region.code.lower()

            # Regional manager
            manager_username = f"manager_{region_slug}"

            manager_user = self._get_or_create_user(
                username=manager_username,
                email=f"{manager_username}@example.com",
                password=demo_password,
                role=UserProfile.Role.SALES_MANAGER,
            )

            manager = self._get_or_create_salesperson(
                user=manager_user,
                employee_code=f"MGR-{region.code}",
                region=region,
            )

            manager_by_region[region.id] = manager

            demo_accounts.append(manager_user)

            # Two salespeople per region
            for salesperson_number in range(1, 3):
                username = (
                    f"sales_{region_slug}_{salesperson_number}"
                )

                user = self._get_or_create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password=demo_password,
                    role=UserProfile.Role.SALESPERSON,
                )

                salesperson = self._get_or_create_salesperson(
                    user=user,
                    employee_code=(
                        f"SP-{region.code}-{salesperson_number}"
                    ),
                    region=region,
                )

                regional_salespeople.append(salesperson)
                demo_accounts.append(user)

        # ---------------------------------------------------------
        # 5. CUSTOMERS
        # ---------------------------------------------------------
        customer_objects = []

        for index in range(1, 81):
            region = region_objects[(index - 1) % len(region_objects)]

            customer, _ = Customer.objects.get_or_create(
                name=f"Customer {index}",
                defaults={
                    "email": f"customer{index}@example.com",
                    "phone": f"99999{index:05d}",
                    "city": f"{region.name} City {index}",
                    "region": region,
                },
            )

            customer_objects.append(customer)

        # ---------------------------------------------------------
        # 6. CREATE TRANSACTIONS
        # ---------------------------------------------------------
        #
        # Transactions are distributed by salesperson.
        # This is important for testing:
        #
        # Salesperson -> own transactions
        # Manager     -> own region
        # Analyst     -> company-wide
        # Admin       -> company-wide
        #
        end_date = timezone.localdate()
        start_date = end_date - timedelta(days=179)

        created_count = 0

        # Group salespeople by region
        salespeople_by_region = {}

        for salesperson in regional_salespeople:
            salespeople_by_region.setdefault(
                salesperson.region_id,
                [],
            ).append(salesperson)

        for day_offset in range(180):
            current_date = start_date + timedelta(days=day_offset)

            weekday = current_date.weekday()

            if weekday < 5:
                daily_transactions = random.randint(8, 14)
            else:
                daily_transactions = random.randint(3, 7)

            for _ in range(daily_transactions):
                # Pick a region first.
                region = random.choice(region_objects)

                # Then salesperson belonging to that region.
                available_salespeople = salespeople_by_region[
                    region.id
                ]

                salesperson = random.choice(
                    available_salespeople
                )

                # Customer from the same region.
                region_customers = [
                    customer
                    for customer in customer_objects
                    if customer.region_id == region.id
                ]

                customer = random.choice(region_customers)

                product = random.choice(product_objects)

                quantity = random.randint(1, 5)

                # Mild trend growth over time.
                trend_multiplier = Decimal(
                    str(1 + (day_offset / 1800))
                )

                unit_price = product.unit_price

                discount_amount = Decimal(
                    str(
                        random.choice(
                            [
                                0,
                                0,
                                0,
                                100,
                                250,
                                500,
                            ]
                        )
                    )
                )

                raw_total = (
                    unit_price
                    * quantity
                    * trend_multiplier
                ).quantize(
                    Decimal("0.01")
                )

                total_amount = max(
                    Decimal("100.00"),
                    raw_total - discount_amount,
                )

                transaction_exists = (
                    SalesTransaction.objects.filter(
                        transaction_date=current_date,
                        customer=customer,
                        product=product,
                        salesperson=salesperson,
                        total_amount=total_amount,
                    ).exists()
                )

                if transaction_exists:
                    continue

                SalesTransaction.objects.create(
                    transaction_date=current_date,
                    customer=customer,
                    product=product,
                    salesperson=salesperson,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_amount=discount_amount,
                    total_amount=total_amount,
                    notes="Seeded demo transaction",
                )

                created_count += 1

        # ---------------------------------------------------------
        # 7. SUMMARY
        # ---------------------------------------------------------
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} sales transactions."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Prepared {len(demo_accounts)} demo users."
            )
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo login accounts:"
            )
        )

        self.stdout.write(
            f"  Admin:      demo_admin / {demo_password}"
        )
        self.stdout.write(
            f"  Analyst:    demo_analyst / {demo_password}"
        )

        for region in region_objects:
            region_slug = region.code.lower()

            self.stdout.write(
                f"  Manager {region.name}: "
                f"manager_{region_slug} / {demo_password}"
            )

            self.stdout.write(
                f"  Sales {region.name} #1: "
                f"sales_{region_slug}_1 / {demo_password}"
            )

            self.stdout.write(
                f"  Sales {region.name} #2: "
                f"sales_{region_slug}_2 / {demo_password}"
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data seeding completed successfully."
            )
        )

    # -------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------

    def _get_or_create_user(
        self,
        *,
        username,
        email,
        password,
        role,
    ):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)

        # Keep demo users active.
        user.is_active = True
        user.email = email

        user.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": role,
            },
        )

        # Explicitly synchronize the demo role.
        if profile.role != role:
            profile.role = role
            profile.save(update_fields=["role", "updated_at"])

        return user

    def _get_or_create_salesperson(
        self,
        *,
        user,
        employee_code,
        region,
    ):
        salesperson, created = (
            SalesPerson.objects.get_or_create(
                employee_code=employee_code,
                defaults={
                    "user": user,
                    "region": region,
                    "is_active": True,
                },
            )
        )

        if not created:
            changed = False

            if salesperson.user_id != user.id:
                salesperson.user = user
                changed = True

            if salesperson.region_id != region.id:
                salesperson.region = region
                changed = True

            if not salesperson.is_active:
                salesperson.is_active = True
                changed = True

            if changed:
                salesperson.save()

        return salesperson