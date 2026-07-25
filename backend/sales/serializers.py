from dataclasses import fields

from rest_framework import serializers

from .models import Customer, Product, Region, SalesPerson, SalesTransaction

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
class CustomerSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    
    class Meta:
        model = Customer
        fields = "__all__"
        
class SalesPersonSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        model = SalesPerson
        fields = "__all__"
        
class SalesTransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    salesperson_code = serializers.CharField(source="salesperson.employee_code", read_only=True)
    region_name = serializers.CharField(source="salesperson.region.name", read_only=True)
    
    class Meta:
        model = SalesTransaction
        fields = "__all__"
        
        
    def validate(self, attrs):
        quantity = attrs.get("quantity")
        unit_price = attrs.get("unit_price")
        discount_amount = attrs.get("discount_amount", 0)
        total_amount = attrs.get("total_amount")
        
        expected_total = (quantity * unit_price) - discount_amount
        if total_amount != expected_total:
            raise serializers.ValidationError(
                {"total_amount": f"Expected total_amount to be {expected_total}"}
            )
            
        return attrs