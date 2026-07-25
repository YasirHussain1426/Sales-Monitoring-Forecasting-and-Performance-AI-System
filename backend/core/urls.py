from django.urls import path
from .views import CurrentUserView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
]