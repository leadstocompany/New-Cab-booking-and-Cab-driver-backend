# Generated by Django 4.2.4 on 2024-10-15 09:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0025_alter_trip_created_at_alter_triprating_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='triprating',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
    ]