# Generated by Django 4.2.4 on 2024-10-15 09:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0009_alter_customersupport_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 408907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='driversupport',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 408907, tzinfo=datetime.timezone.utc)),
        ),
    ]
