# Generated by Django 5.1.4 on 2025-04-14 05:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wallets", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wallet",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 4, 14, 5, 45, 39, 420964, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
