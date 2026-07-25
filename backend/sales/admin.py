from django.contrib import admin
from .models import Customer, Product, Region, SalesPerson, SalesTransaction

# Register your models here.

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")
    
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "unit_price", "is_active")
    search_fields = ("name", "sku", "category")
    list_filter = ("is_active", "category")
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "city", "region")
    search_fields = ("name", "email", "city")
    list_filter = ("region",)
    
@admin.register(SalesPerson)
class SalesPersonAdmin(admin.ModelAdmin):
    list_display = ("employee_code", "user", "region", "is_active")
    search_fields = ("employee_code", "user__username")
    list_filter = ("region", "is_active")
    
@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction_date",
        "customer",
        "product",
        "salesperson",
        "quantity",
        "total_amount",
    )
    search_fields = ("customer__name", "product__name", "salesperson__employee_code")
    list_filter = ("transaction_date", "product", "salesperson")