# Generated by Django 4.2.4 on 2024-10-07 08:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0015_alter_city_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 7, 8, 20, 21, 941285, tzinfo=datetime.timezone.utc)),
        ),
    ]
