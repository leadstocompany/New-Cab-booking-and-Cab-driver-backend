from django.db import models
from utility.model import BaseModel
from accounts.models import User
from cabs.models import *
from admin_api.models import FeedbackSetting
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
# from trips.tasks import send_trip_notification
# Create your models here.


class Trip(BaseModel):
    TRIP_STATUS = (('REQUESTED', 'REQUESTED'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), 
                    ('BOOKED', 'BOOKED'), ('CANCELLED', 'CANCELLED'),
                   ('ON_TRIP', 'ON_TRIP'), ('COMPLETED', 'COMPLETED'))

    customer = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='cutomer_trips')
    driver = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name='driver_trips')
    cab = models.ForeignKey(
        Vehicle, on_delete=models.PROTECT, null=True, blank=True, related_name='trips')
    status = models.CharField(
        choices=TRIP_STATUS, max_length=74, null=True, blank=True)
    source = models.CharField(max_length=5000, null=True, blank=True)
    destination = models.CharField(max_length=5000, null=True, blank=True)
    pickup_latitude=models.CharField(max_length=50, null=True, blank=True)
    pickup_longitude=models.CharField(max_length=50, null=True, blank=True)
    dropup_latitude=models.CharField(max_length=50, null=True, blank=True)
    dropup_longitude=models.CharField(max_length=50, null=True, blank=True)
    # distance = models.CharField(max_length=11, null=True, blank=True)
    distance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    time = models.CharField(max_length=74, null=True, blank=True)
    ride_type = models.ForeignKey(CabClass, on_delete=models.CASCADE)
    otp_count = models.PositiveIntegerField(default=1)
    order_id = models.TextField(max_length=74, null=True, blank=True)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=0, null=True, blank=True)
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    canceled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='canceled_trips'
    )
    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    payment_type= models.CharField(max_length=255, null=True, blank=True)
    waiting_time=models.CharField(max_length=4, null=True, blank=True)
    waiting_charge= models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],default=0, null=True, blank=True)
    total_fare= models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],default=0, null=True, blank=True)
    payment_status=models.CharField(max_length=255, null=True, blank=True)
    driver_arrived_at_pickup_time=models.DateTimeField(null=True, blank=True)
    ride_start_time=models.DateTimeField(null=True, blank=True)
    ride_end_time=models.DateTimeField(null=True, blank=True)
    
      
    def __str__(self):
        return self.source


class TripRating(BaseModel):
    feedbacksetting = models.ForeignKey(FeedbackSetting, on_delete=models.PROTECT, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True ,related_name='cutomer')
    driver = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='driver')
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT)
    star = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.trip.source

# Register signals
# import trips.signals  # Ensure this import is at the bottom