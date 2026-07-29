from django.contrib import admin

from .models import SalesTarget


@admin.register(SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = ("target_type", "target_amount", "period_start", "period_end")
    list_filter = ("target_type", "period_start", "period_end")
    search_fields = ("region__name", "product__name", "salesperson__employee_code")