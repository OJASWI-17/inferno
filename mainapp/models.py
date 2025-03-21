from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)  # Default balance

    def __str__(self):
        return f"{self.user.username}'s Profile"

class StockDetail(models.Model):
    stock = models.CharField(max_length=10)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.stock
    
    
    
    


class UserStock(models.Model):
    ORDER_TYPES = [
        ('MARKET', 'Market'),
        ('LIMIT', 'Limit'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=0)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_type = models.CharField(max_length=6, choices=ORDER_TYPES, default='MARKET')  # New field

    def __str__(self):
        return f"{self.user.username} - {self.stock} ({self.quantity} shares)"



class LimitOrder(models.Model):
    ORDER_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)  # Add created_at field

    def __str__(self):
        return f"{self.order_type} {self.quantity} shares of {self.stock} at ${self.price}"
    
    
    
    
    
    