from django.db import models

from sales.models import Product, Region, SalesPerson
from targets.models import SalesTarget


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ("forecast_target_shortfall", "Forecast Target Shortfall"),
        ("forecast_error_high", "Forecast Error High"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
    ]

    SCOPE_TYPE_CHOICES = [
        ("overall", "Overall"),
        ("region", "Region"),
        ("product", "Product"),
        ("salesperson", "Salesperson"),
    ]

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    title = models.CharField(max_length=255)
    message = models.TextField()

    scope_type = models.CharField(max_length=20, choices=SCOPE_TYPE_CHOICES, default="overall")
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
    )
    salesperson = models.ForeignKey(
        SalesPerson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alerts",
    )
    target = models.ForeignKey(
        SalesTarget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )

    triggered_for_date = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alert_type} - {self.scope_type} - {self.triggered_for_date}"