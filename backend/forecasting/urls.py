from django.urls import path

from .views import (
    DailySalesForecastView,
    ForecastVsActualView,
    ForecastVsTargetView,
)

urlpatterns = [
    path("daily/", DailySalesForecastView.as_view(), name="daily-sales-forecast"),
    path("forecast-vs-actual/", ForecastVsActualView.as_view(), name="forecast-vs-actual"),
    path("forecast-vs-target/", ForecastVsTargetView.as_view(), name="forecast-vs-target"),
]