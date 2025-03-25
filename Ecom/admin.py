from django.contrib import admin
from .models import Products, Category, Cart, Order , CartItem ,OrderItem 
# Register your models here.
admin.site.register(Products)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
