
from rest_framework import viewsets
from datetime import datetime
from rest_framework.exceptions import ValidationError
from .models import Customer, Product, Region, SalesPerson, SalesTransaction
from .serializers import (
    CustomerSerializer,
    ProductSerializer,
    RegionSerializer,
    SalesPersonSerializer,
    SalesTransactionSerializer,
)
from django.db.models import Avg, Count, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import TruncDate
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related("region").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
class SalesPersonViewSet(viewsets.ModelViewSet):
    queryset = SalesPerson.objects.select_related("user", "region").all()
    serializer_class = SalesPersonSerializer
    permission_classes = [IsAuthenticated]
    
class SalesTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = SalesTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SalesTransaction.objects.select_related(
            "customer",
            "product",
            "salesperson",
            "salesperson__region",
        ).all()

        queryset = filter_transaction_by_date(self.request, queryset)

        region = self.request.GET.get("region")
        product = self.request.GET.get("product")
        salesperson = self.request.GET.get("salesperson")

        if region:
            queryset = queryset.filter(salesperson__region_id=region)

        if product:
            queryset = queryset.filter(product_id=product)

        if salesperson:
            queryset = queryset.filter(salesperson_id=salesperson)

        return queryset.order_by("-transaction_date", "-id")
    
class SalesDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = filter_transaction_by_date(request, SalesTransaction.objects.all())
        
        summary = queryset.aggregate(
            total_revenue=Sum("total_amount"),
            total_transactions=Count("id"),
            total_quantity=Sum("quantity"),
            average_order_value=Avg("total_amount"),
        )
        
        data = {
            "total_revenue": summary["total_revenue"] or 0,
            "total_transactions": summary["total_transactions"] or 0,
            "total_quantity": summary["total_quantity"] or 0,
            "average_order_value": summary["average_order_value"] or 0,
        }    
        return Response(data)
    
    
class SalesDashboardTrendView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = filter_transaction_by_date(request, SalesTransaction.objects.all())
        
        trends = (
            queryset
            .annotate(day=TruncDate("transaction_date"))
            .values("day")
            .annotate(total_sales=Sum("total_amount"))
            .order_by("day")
        )
        data = [
            {
                "day": item["day"],
                "total_sales": item["total_sales"] or 0,
            }
            for item in trends
        ]
        return Response(data)
    
class SalesByRegionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = filter_transaction_by_date(request, SalesTransaction.objects.all())
        
        region_data = (
            queryset
            .values("salesperson__region__name")
            .annotate(total_sales=Sum("total_amount"))
            .order_by("-total_sales")
        )
        
        data = [
            {
                "region": item["salesperson__region__name"] or "Unknown",
                "total_sales": item["total_sales"] or 0,
            }
            for item in region_data
        ]
        return Response(data)
    
class TopProductsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = filter_transaction_by_date(request, SalesTransaction.objects.all())
        top_products = (
            queryset
            .values("product__name", "product__sku")
            .annotate(total_sales=Sum("total_amount"))
            .order_by("-total_sales")[:5]
        )

        data = [
            {
                "product_name": item["product__name"],
                "sku": item["product__sku"],
                "total_sales": item["total_sales"] or 0,
            }
            for item in top_products
        ]
        return Response(data)
    
def filter_transaction_by_date(request, queryset):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            queryset = queryset.filter(transaction_date__gte=parsed_start)
        except ValueError:
            raise ValidationError({"start_date": "Use YYYY-MM-DD format."})
        
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(transaction_date__lte=parsed_end)
        except ValueError:
            raise ValidationError({"end_date": "Use YYYY-MM-DD format."})
        
    return queryset