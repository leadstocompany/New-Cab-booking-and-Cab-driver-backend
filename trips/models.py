from django.db import models
from utility.model import BaseModel
from accounts.models import User
from cabs.models import *
from admin_api.models import FeedbackSetting
# Create your models here.


class Trip(BaseModel):
    TRIP_STATUS = (('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), 
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
    source = models.CharField(max_length=74, null=True, blank=True)
    destination = models.CharField(max_length=74, null=True, blank=True)
    distance = models.CharField(max_length=11, null=True, blank=True)
    timing = models.CharField(max_length=74, null=True, blank=True)
    ride_type = models.ForeignKey(CabClass, on_delete=models.CASCADE)
    otp_count = models.PositiveIntegerField(default=1)
    order_id = models.TextField(max_length=74, null=True, blank=True)
    
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
        return self.trip

class DriverPricingRatio(BaseModel):
    ratio = models.FloatField("Ratio")

    def __str__(self):
        return self.ratio