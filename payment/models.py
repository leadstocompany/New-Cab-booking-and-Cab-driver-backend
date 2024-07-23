from django.db import models
from django.db import models
from utility.model import BaseModel
from trips.models import Trip
from django.core.validators import MinValueValidator
from decimal import Decimal
# Create your models here.
class Payment(BaseModel):
    trip=models.ForeignKey(Trip,  on_delete=models.PROTECT)
    amount=models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=10, default='usd')
    payment_type=models.CharField(max_length=255, null=True, blank=True)
    payment_id=models.CharField(max_length=255, null=True, blank=True)
    status_choices = (
        ('PAID', 'PAID'),
        ('PENDING', 'PENDING'),
        ('FAILED', 'FAILED'),
        ('REFUNDED', 'REFUNDED'),
    )
    payment_status = models.CharField(max_length=15, choices=status_choices)
    def __str__(self):
        return self.trip 