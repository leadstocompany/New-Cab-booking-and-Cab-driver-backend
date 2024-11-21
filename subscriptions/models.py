from django.db import models
from accounts.models import User, Driver
from datetime import datetime
from django.utils import timezone
from cabs.models import CabClass
from datetime import datetime
from django.utils.timezone import now
from django.utils import timezone
# Create your models here.


class SubscriptionPlan(models.Model):
   
    vehicle_class = models.ForeignKey(CabClass, on_delete=models.CASCADE, unique=False, related_name='subscription_plans')
    plan_name = models.CharField(max_length=500)
    days = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    original_price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.localtime(timezone.now()))
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plan_name} - {self.vehicle_class.cab_class} - {self.price}"

    class Meta:
        db_table = 'subscription_plan'
        # unique_together = ['vehicle_class']





class Subscriptions(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    subcribe_date=models.DateTimeField()
    expire_date=models.DateTimeField()
    status_choices = (
        ('PAID', 'PAID'),
        ('PENDING', 'PENDING'),
        ('FAILED', 'FAILED'),
        ('REFUNDED', 'REFUNDED'),
    )
    
    payment_status = models.CharField(max_length=15, choices=status_choices)
    number_of_time_subscribe=models.IntegerField(default=0)
    payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    created_at=models.DateTimeField(default=timezone.localtime(timezone.now()))
    # updated_at=models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    def __str__(self):
        return f"{self.driver.phone} - {self.plan.plan_name}"
    class Meta:
        db_table = 'subscriptions'
    def is_expired(self):
        """Check if the subscription is expired."""
        return now() > self.expire_date




class Subscription_Logs(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    subcribe_date=models.DateTimeField()
    expire_date=models.DateTimeField()
    status_choices = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    payment_status = models.CharField(max_length=15, choices=status_choices)
    payment_id = models.CharField(max_length= 55, default=None, null=True, blank=True)
    created_at=models.DateTimeField(default=timezone.localtime(timezone.now()))
    # updated_at=models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.driver.phone} - {self.plan}"
    class Meta:
        db_table = 'subscription_logs'


