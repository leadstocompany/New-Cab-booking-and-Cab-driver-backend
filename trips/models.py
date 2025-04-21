from django.db import models
from utility.model import BaseModel
from accounts.models import User
from cabs.models import *
from admin_api.models import FeedbackSetting
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utility.util import calculate_percentage_change, generate_six_digit_uuid

# from trips.tasks import send_trip_notification
# Create your models here.


class Trip(BaseModel):
    TRIP_STATUS = (('REQUESTED', 'REQUESTED'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), 
                    ('BOOKED', 'BOOKED'), ('CANCELLED', 'CANCELLED'),
                   ('ON_TRIP', 'ON_TRIP'), ('COMPLETED', 'COMPLETED'))

    trip_id = models.CharField(max_length=500, null=True, blank=True, default=generate_six_digit_uuid)
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
    ride_type = models.ForeignKey(CabClass, on_delete=models.CASCADE, null=True, blank=True)
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
    coupon_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.source)

    @classmethod
    def get_weekly_income_stats(cls):
        today = timezone.localtime().date()
        first_day = today.replace(day=1)

        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(
                days=1
            )
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        weekly_income = []

        current_date = first_day
        week_start = current_date

        while current_date <= last_day:
            week_end = min(week_start + timedelta(days=6), last_day)
            week_label = f"{week_start.day}-{week_end.day}"

            income = (
                cls.objects.filter(
                    status="COMPLETED",
                    ride_end_time__date__gte=week_start,
                    ride_end_time__date__lte=week_end,
                    payment_status="paid",
                ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
                or 0
            )

            weekly_income.append(
                {
                    "name": week_label,
                    "amt": income,
                }
            )
            week_start = week_end + timedelta(days=1)
            current_date = week_start

        return weekly_income

    @classmethod
    def get_income_stats(cls):
        today = timezone.localtime().date()

        # Today's income
        today_income = (
            cls.objects.filter(
                status="COMPLETED", ride_end_time__date=today, payment_status="paid"
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        # This week's income
        week_start = today - timedelta(days=today.weekday())
        week_income = (
            cls.objects.filter(
                status="COMPLETED",
                ride_end_time__date__gte=week_start,
                ride_end_time__date__lte=today,
                payment_status="paid",
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        # This month's income
        month_income = (
            cls.objects.filter(
                status="COMPLETED",
                ride_end_time__date__year=today.year,
                ride_end_time__date__month=today.month,
                payment_status="paid",
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        # This year's income
        year_income = (
            cls.objects.filter(
                status="COMPLETED",
                ride_end_time__date__year=today.year,
                payment_status="paid",
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        # Month-wise income for current year
        monthly_income = []
        for month in range(1, 13):
            income = (
                cls.objects.filter(
                    status="COMPLETED",
                    ride_end_time__date__year=today.year,
                    ride_end_time__date__month=month,
                    payment_status="paid",
                ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
                or 0
            )
            monthly_income.append(
                {"name": datetime(today.year, month, 1).strftime("%b"), "amt": income}
            )

        return {
            "today_income": today_income,
            "week_income": week_income,
            "month_income": month_income,
            "year_income": year_income,
            "monthly_breakdown": monthly_income,
            "weekly_breakdown": cls.get_weekly_income_stats(),
        }

    @classmethod
    def get_booked_trips_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_booked = cls.objects.filter(
            status__in=["BOOKED", "ON_TRIP"], created_at__gte=current_month_start
        ).count()

        last_month_booked = cls.objects.filter(
            status__in=["BOOKED", "ON_TRIP"],
            created_at__gte=last_month_start,
            created_at__lt=current_month_start,
        ).count()

        return {
            "count": current_booked,
            "percentage": calculate_percentage_change(
                last_month_booked, current_booked
            ),
        }

    @classmethod
    def get_cancelled_trips_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_cancelled = cls.objects.filter(
            status="CANCELLED", created_at__gte=current_month_start
        ).count()

        last_month_cancelled = cls.objects.filter(
            status="CANCELLED",
            created_at__gte=last_month_start,
            created_at__lt=current_month_start,
        ).count()

        return {
            "count": current_cancelled,
            "percentage": calculate_percentage_change(
                last_month_cancelled, current_cancelled
            ),
        }

    @classmethod
    def get_completed_trips_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_completed = cls.objects.filter(
            status="COMPLETED", ride_end_time__gte=current_month_start
        ).count()

        last_month_completed = cls.objects.filter(
            status="COMPLETED",
            ride_end_time__gte=last_month_start,
            ride_end_time__lt=current_month_start,
        ).count()

        return {
            "count": current_completed,
            "percentage": calculate_percentage_change(
                last_month_completed, current_completed
            ),
        }

    @classmethod
    def get_total_earnings_stats(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_earnings = (
            cls.objects.filter(
                status="COMPLETED",
                payment_status="paid",
                ride_end_time__gte=current_month_start,
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        last_month_earnings = (
            cls.objects.filter(
                status="COMPLETED",
                payment_status="paid",
                ride_end_time__gte=last_month_start,
                ride_end_time__lt=current_month_start,
            ).aggregate(models.Sum("total_fare"))["total_fare__sum"]
            or 0
        )

        return {
            "amount": current_earnings,
            "percentage": calculate_percentage_change(
                last_month_earnings, current_earnings
            ),
        }


class TripRating(BaseModel):
    feedbacksetting = models.ForeignKey(FeedbackSetting, on_delete=models.PROTECT, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True ,related_name='cutomer')
    driver = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='driver')
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT)
    star = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.trip.source


class PickupRadius(models.Model):
    id = models.AutoField(primary_key=True)
    radius = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Pickup Radius: {self.radius} km"

# Register signals
# import trips.signals  # Ensure this import is at the bottom
