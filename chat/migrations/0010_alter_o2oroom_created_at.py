# Generated by Django 4.2.4 on 2024-10-04 13:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_o2oroom_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='o2oroom',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 13, 59, 5, 469045, tzinfo=datetime.timezone.utc)),
        ),
    ]
