# Generated by Django 4.2.4 on 2024-07-22 13:56

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0011_remove_trip_scheduled_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DriverPricingRatio',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='scheduled_time',
            new_name='scheduled_datetime',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='timing',
            new_name='time',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='trip_rent_price',
        ),
        migrations.AddField(
            model_name='trip',
            name='payment_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='payment_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='rent_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AddField(
            model_name='trip',
            name='total_fare',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AddField(
            model_name='trip',
            name='waiting_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AddField(
            model_name='trip',
            name='waiting_time',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
