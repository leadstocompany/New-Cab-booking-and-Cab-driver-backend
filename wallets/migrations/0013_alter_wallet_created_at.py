# Generated by Django 4.2.4 on 2024-10-15 09:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0012_alter_wallet_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 396910, tzinfo=datetime.timezone.utc)),
        ),
    ]