# Generated by Django 4.2.4 on 2024-10-04 14:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sos', '0003_soshelprequest_last_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soshelprequest',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 14, 0, 41, 869578, tzinfo=datetime.timezone.utc)),
        ),
    ]
