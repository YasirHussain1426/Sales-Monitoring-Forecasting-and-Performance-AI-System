from django.core.exceptions import ValidationError
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

    def clean(self):
        scope_values = {
            "region": self.region_id,
            "product": self.product_id,
            "salesperson": self.salesperson_id,
        }

        if self.period_end < self.period_start:
            raise ValidationError({"period_end": "period_end must be on or after period_start."})

        if self.target_type == "overall":
            if any(scope_values.values()):
                raise ValidationError("Overall target cannot have region, product, or salesperson.")
            return

        required_scope = scope_values.get(self.target_type)
        if not required_scope:
            raise ValidationError({self.target_type: f"{self.target_type} target requires its matching scope."})

        extra_scopes = [
            key for key, value in scope_values.items()
            if key != self.target_type and value is not None
        ]
        if extra_scopes:
            raise ValidationError(
                f"{self.target_type} target cannot include extra scopes: {', '.join(extra_scopes)}."
            )

    def __str__(self):
        return f"{self.target_type} target - {self.target_amount}"