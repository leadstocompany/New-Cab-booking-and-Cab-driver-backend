# Generated by Django 4.2.4 on 2024-10-07 08:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_alter_bill_payment_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill_payment',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 7, 8, 20, 21, 941285, tzinfo=datetime.timezone.utc)),
        ),
    ]
