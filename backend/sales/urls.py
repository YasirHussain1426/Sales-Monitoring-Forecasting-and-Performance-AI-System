from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet,
    ProductViewSet,
    RegionViewSet,
    SalesByRegionView,
    SalesDashboardSummaryView,
    SalesDashboardTrendView,
    SalesPersonViewSet,
    SalesTransactionViewSet,
    TopProductsView,
)

router = DefaultRouter()
router.register("regions", RegionViewSet)
router.register("products", ProductViewSet)
router.register("customer", CustomerViewSet)
router.register("salespeople", SalesPersonViewSet)
router.register("transactions", SalesTransactionViewSet, basename="transactions")


urlpatterns = [
    path("dashboard/summary/", SalesDashboardSummaryView.as_view(), name="sales-dashboard-summary"),
    path("dashboard/trends/", SalesDashboardTrendView.as_view(), name="sales-dashboard-trends"),
    path("dashboard/by-region/", SalesByRegionView.as_view(), name="sales-by-region"),
    path("dashboard/top-products/", TopProductsView.as_view(), name="top-products"),
]

urlpatterns += router.urls
