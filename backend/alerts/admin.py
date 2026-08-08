from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "alert_type",
        "severity",
        "status",
        "scope_type",
        "triggered_for_date",
        "created_at",
    )
    list_filter = (
        "alert_type",
        "severity",
        "status",
        "scope_type",
        "triggered_for_date",
    )
    search_fields = ("title", "message")