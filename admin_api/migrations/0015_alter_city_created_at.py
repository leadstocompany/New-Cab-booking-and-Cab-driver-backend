# Generated by Django 4.2.4 on 2024-10-04 16:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0014_alter_city_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 16, 17, 16, 94524, tzinfo=datetime.timezone.utc)),
        ),
    ]