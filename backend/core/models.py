from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        COMPANY_ADMIN = "company_admin", "Company Admin"
        SALES_MANAGER = "sales_manager", "Sales Manager"
        SALESPERSON = "salesperson", "Salesperson"
        ANALYST = "analyst", "Analyst"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.ANALYST,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"