# Generated by Django 4.2.4 on 2024-10-04 07:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_rename_payment_bill_payment_alter_bill_payment_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill_payment',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 7, 38, 56, 16167, tzinfo=datetime.timezone.utc)),
        ),
    ]