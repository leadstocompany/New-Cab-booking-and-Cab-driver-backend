# Generated by Django 4.2.4 on 2024-10-04 07:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0011_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 7, 38, 56, 16167, tzinfo=datetime.timezone.utc)),
        ),
    ]
