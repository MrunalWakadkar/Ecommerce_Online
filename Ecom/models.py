from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import now

class Category(models.Model):
    name= models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Products(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products')
    brand = models.CharField(max_length=100)
    price = models.IntegerField()
    # CATEGORY_LIST = [('T-shirt', 'T-shirt'), ('Hoodies', 'Hoodies'),('Shirt,', 'Shirt'),('Jacket', 'Jacket')]
    # category = models.CharField(max_length=255, choices=CATEGORY_LIST, default='T-shirt')
    category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    desc = models.TextField()
    specification = models.TextField()

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user has one cart
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        return sum(item.total_price for item in self.cartitem_set.all())

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Ensure this field exists
    product = models.ForeignKey("Products", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.price 
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ('PayPal', 'PayPal'),
        ('Credit/Debit Card', 'Credit/Debit Card'),
        ('Cash on Delivery', 'Cash on Delivery'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Ecom.Products", on_delete=models.CASCADE)  # Assuming "shop.Product" exists
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
    



