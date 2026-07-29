import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from sales.models import Customer, Product, Region, SalesPerson, SalesTransaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seed realistic demo sales data"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding demo sales data..."))

        regions_data = [
            {"name": "North", "code": "NORTH"},
            {"name": "South", "code": "SOUTH"},
            {"name": "East", "code": "EAST"},
            {"name": "West", "code": "WEST"},
        ]

        products_data = [
            {"name": "Laptop", "sku": "LP100", "category": "Electronics", "unit_price": Decimal("75000.00")},
            {"name": "Mouse", "sku": "MS200", "category": "Accessories", "unit_price": Decimal("1200.00")},
            {"name": "Keyboard", "sku": "KB300", "category": "Accessories", "unit_price": Decimal("2500.00")},
            {"name": "Monitor", "sku": "MN400", "category": "Electronics", "unit_price": Decimal("18000.00")},
            {"name": "Printer", "sku": "PR500", "category": "Office", "unit_price": Decimal("14000.00")},
            {"name": "Desk Chair", "sku": "DC600", "category": "Furniture", "unit_price": Decimal("8500.00")},
            {"name": "Tablet", "sku": "TB700", "category": "Electronics", "unit_price": Decimal("32000.00")},
            {"name": "Webcam", "sku": "WC800", "category": "Accessories", "unit_price": Decimal("3500.00")},
            {"name": "Headset", "sku": "HS900", "category": "Accessories", "unit_price": Decimal("4200.00")},
            {"name": "Router", "sku": "RT1000", "category": "Networking", "unit_price": Decimal("6800.00")},
        ]

        region_objects = []
        for region_data in regions_data:
            region, _ = Region.objects.get_or_create(
                code=region_data["code"],
                defaults={"name": region_data["name"]},
            )
            region_objects.append(region)

        product_objects = []
        for product_data in products_data:
            product, _ = Product.objects.get_or_create(
                sku=product_data["sku"],
                defaults={
                    "name": product_data["name"],
                    "category": product_data["category"],
                    "unit_price": product_data["unit_price"],
                    "is_active": True,
                },
            )
            product_objects.append(product)

        salesperson_objects = []
        for index, region in enumerate(region_objects, start=1):
            username = f"sales{index}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "is_active": True,
                },
            )
            if created:
                user.set_password("Password123")
                user.save()

            salesperson, _ = SalesPerson.objects.get_or_create(
                employee_code=f"EMP{1000 + index}",
                defaults={
                    "user": user,
                    "region": region,
                    "is_active": True,
                },
            )
            salesperson_objects.append(salesperson)

        customer_objects = []
        for index in range(1, 51):
            region = random.choice(region_objects)
            customer, _ = Customer.objects.get_or_create(
                name=f"Customer {index}",
                defaults={
                    "email": f"customer{index}@example.com",
                    "phone": f"99999{index:05d}",
                    "city": f"City {index}",
                    "region": region,
                },
            )
            customer_objects.append(customer)

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=179)

        created_count = 0

        for day_offset in range(180):
            current_date = start_date + timedelta(days=day_offset)

            weekday = current_date.weekday()
            daily_transactions = random.randint(3, 8) if weekday < 5 else random.randint(1, 4)

            for _ in range(daily_transactions):
                product = random.choice(product_objects)
                customer = random.choice(customer_objects)
                salesperson = random.choice(salesperson_objects)

                base_quantity = random.randint(1, 5)
                region_multiplier = Decimal(str(random.uniform(0.9, 1.15)))
                trend_multiplier = Decimal(str(1 + (day_offset / 1800)))

                unit_price = product.unit_price
                discount_amount = Decimal(str(random.choice([0, 0, 0, 100, 250, 500])))
                quantity = base_quantity

                raw_total = (unit_price * quantity * region_multiplier * trend_multiplier).quantize(Decimal("0.01"))
                total_amount = max(Decimal("100.00"), raw_total - discount_amount)

                transaction_exists = SalesTransaction.objects.filter(
                    transaction_date=current_date,
                    customer=customer,
                    product=product,
                    salesperson=salesperson,
                    total_amount=total_amount,
                ).exists()

                if not transaction_exists:
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

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} sales transactions."))
        self.stdout.write(self.style.SUCCESS("Demo data seeding completed successfully."))