from django.db import models
from django.conf import settings

# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
        

class Region(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    
    class Meta:
        ordering = ["name"]
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    
class Product(TimeStampedModel):
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["name"]
        
        
    def __str__(self):
        return f"{self.name} - {self.sku}"
    

class Customer(TimeStampedModel):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="customers")
    
    class Meta:
        ordering = ["name"]
        
    def __str__(self):
        return self.name
    
class SalesPerson(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sales_profile",
    )
    employee_code = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="salespeople")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["employee_code"]
        
    def __str__(self):
        return self.employee_code
    
class SalesTransaction(TimeStampedModel):
    transaction_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="transactions")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions")
    salesperson = models.ForeignKey(
        SalesPerson,
        on_delete=models.PROTECT,
        related_name="transactions"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    
    
    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        
    def __str__(self):
        return f"TX-{self.id} - {self.transaction_date}"
    
    
        