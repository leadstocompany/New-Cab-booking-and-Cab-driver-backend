# Generated by Django 4.2.4 on 2024-07-19 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0010_trip_cancel_reason_trip_canceled_by_trip_otp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='scheduled_date',
        ),
    ]
