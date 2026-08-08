from django.urls import path

from .views import AlertListView, ResolveAlertView, RunAlertRulesView

urlpatterns = [
    path("", AlertListView.as_view(), name="alert-list"),
    path("rules/run/", RunAlertRulesView.as_view(), name="run-alert-rules"),
    path("<int:alert_id>/resolve/", ResolveAlertView.as_view(), name="resolve-alert"),
]