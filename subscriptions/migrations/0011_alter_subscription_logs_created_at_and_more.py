# Generated by Django 4.2.4 on 2024-10-15 07:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0010_alter_subscription_logs_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription_logs',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 7, 2, 54, 204874, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 7, 2, 54, 203873, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 7, 2, 54, 204874, tzinfo=datetime.timezone.utc)),
        ),
    ]
