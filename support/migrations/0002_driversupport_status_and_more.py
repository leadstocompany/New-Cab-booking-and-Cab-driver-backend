# Generated by Django 5.1.4 on 2025-02-27 11:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("support", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="driversupport",
            name="status",
            field=models.CharField(db_default="raised"),
        ),
        migrations.AlterField(
            model_name="customersupport",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 27, 11, 49, 31, 7567, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="driversupport",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 27, 11, 49, 31, 6568, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
