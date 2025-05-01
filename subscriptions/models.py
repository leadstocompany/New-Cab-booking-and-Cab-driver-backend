from django.db import models
from accounts.models import User, Driver
from datetime import datetime
from django.utils import timezone
from cabs.models import CabClass
from datetime import datetime
from django.utils.timezone import now
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from utility.util import calculate_percentage_change
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


from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta

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

    class Meta:
        db_table = 'subscriptions'

    def is_expired(self):
        """Check if the subscription is expired."""
        return now() > self.expire_date

    @classmethod
    def get_today_income(cls):
        today = timezone.localtime().date()
        return (
            cls.objects.filter(created_at__date=today, payment_status="PAID").aggregate(
                total=Sum("pay_amount")
            )["total"]
            or 0
        )

    @classmethod
    def get_this_week_income(cls):
        today = timezone.localtime()
        start_of_week = today - timedelta(days=today.weekday())
        return (
            cls.objects.filter(
                created_at__gte=start_of_week, payment_status="PAID"
            ).aggregate(total=Sum("pay_amount"))["total"]
            or 0
        )

    @classmethod
    def get_this_month_income(cls):
        today = timezone.localtime()
        start_of_month = today.replace(day=1)
        return (
            cls.objects.filter(
                created_at__gte=start_of_month, payment_status="PAID"
            ).aggregate(total=Sum("pay_amount"))["total"]
            or 0
        )

    @classmethod
    def get_this_year_income(cls):
        today = timezone.localtime()
        start_of_year = today.replace(month=1, day=1)
        return (
            cls.objects.filter(
                created_at__gte=start_of_year, payment_status="PAID"
            ).aggregate(total=Sum("pay_amount"))["total"]
            or 0
        )

    @classmethod
    def get_total_income(cls):
        today = timezone.now()
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)

        current_year_earnings = (
            cls.objects.filter(
                payment_status="PAID", created_at__gte=current_month_start
            ).aggregate(models.Sum("pay_amount"))["pay_amount__sum"]
            or 0
        )

        last_year_earnings = (
            cls.objects.filter(
                payment_status="PAID",
                created_at__gte=last_month_start,
                created_at__lt=current_month_start,
            ).aggregate(models.Sum("pay_amount"))["pay_amount__sum"]
            or 0
        )

        return {
            "amount": current_year_earnings,
            "percentage": calculate_percentage_change(
                last_year_earnings, current_year_earnings
            ),
        }

    @classmethod
    def get_monthly_income_breakdown(cls):
        monthly_income = []
        today = timezone.now()
        for month in range(1, 13):
            income = (
                cls.objects.filter(
                    payment_status="PAID",
                    created_at__date__year=today.year,
                    created_at__date__month=month,
                ).aggregate(models.Sum("pay_amount"))["pay_amount__sum"]
                or 0
            )
            monthly_income.append(
                {"name": datetime(today.year, month, 1).strftime("%b"), "amt": income}
            )
        return monthly_income

    @classmethod
    def get_weekly_income_breakdown(cls):
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
                    payment_status="PAID",
                    created_at__date__gte=week_start,
                    created_at__date__lte=week_end,
                ).aggregate(models.Sum("pay_amount"))["pay_amount__sum"]
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
