from django.db import models
from accounts.models import Driver, Customer
from django.utils import timezone
# Create your models here.

class DriverSupport(models.Model):
    driver = models.ForeignKey(Driver, related_name='driver_support',on_delete=models.PROTECT)
    subject=models.CharField(max_length=500)
    massege=models.TextField()
    created_at=models.DateTimeField(default=timezone.localtime(timezone.now()))
    def __str__(self):
        return f'{self.subject}'


class CustomerSupport(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_support',on_delete=models.PROTECT)
    subject=models.CharField(max_length=500)
    massege=models.TextField()
    created_at=models.DateTimeField(default=timezone.localtime(timezone.now()))
    def __str__(self):
        return f'{self.subject}'
    
    
