from django.db import models
from accounts.models import Driver, Customer
# Create your models here.

class DriverSupport(models.Model):
    driver = models.ForeignKey(Driver, related_name='driver_support',on_delete=models.PROTECT)
    subject=models.CharField(max_length=500)
    massege=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.subject}'



    
