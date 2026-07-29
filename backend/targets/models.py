from django.db import models

from sales.models import Product, Region, SalesPerson


class SalesTarget(models.Model):
    TARGET_TYPE_CHOICES = [
        ("overall", "Overall"),
        ("region", "Region"),
        ("product", "Product"),
        ("salesperson", "Salesperson"),
    ]

    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targets",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targets",
    )
    salesperson = models.ForeignKey(
        SalesPerson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targets",
    )

    class Meta:
        ordering = ["-period_start", "target_type"]

    def __str__(self):
        return f"{self.target_type} target - {self.target_amount}"