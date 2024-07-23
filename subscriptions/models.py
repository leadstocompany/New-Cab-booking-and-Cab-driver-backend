from django.db import models
from accounts.models import User, Driver
from datetime import datetime
from django.utils import timezone
# Create your models here.
class SubscriptionPlan(models.Model):
    plan_name=models.CharField(max_length=500, null=True, blank=True)
    ride_numbers=models.PositiveIntegerField(default=0)
    price=models.PositiveIntegerField(default=0)
    discount=models.PositiveIntegerField(default=0)
    original_price=models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # created_at=models.DateTimeField(default=timezone.now)
    # updated_at=models.DateTimeField(default=timezone.now)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.price}"
    class Meta:
        db_table = 'subscription_plan'




class Subscription(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    complated_rides=models.PositiveIntegerField(default=0)
    pending_rides=models.PositiveIntegerField(default=0)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
   
    status_choices = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    payment_status = models.CharField(max_length=15, choices=status_choices)
    number_of_time_subscribe=models.IntegerField(default=0)
    payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    # order_id = models.CharField(max_length=55 , default=" ", null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.driver.username} - {self.plan}"
    class Meta:
        db_table = 'subscription'




class Subscriptions_Logs(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    status_choices = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    payment_status = models.CharField(max_length=15, choices=status_choices)
    payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    # order_id = models.CharField(max_length=55 , default=" ", null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.driver.username} - {self.plan}"
    class Meta:
        db_table = 'subscription_logs'


