# Generated by Django 4.2.4 on 2024-10-04 07:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 7, 38, 56, 126936, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='driversupport',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 7, 38, 56, 125937, tzinfo=datetime.timezone.utc)),
        ),
    ]
