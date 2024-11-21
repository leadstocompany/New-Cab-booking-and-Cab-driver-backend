# Generated by Django 4.2.4 on 2024-10-15 09:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabs', '0038_alter_cabclass_created_at_alter_cabtype_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabclass',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='cabtype',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='vehiclemaker',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='vehiclemodel',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 15, 9, 24, 37, 366907, tzinfo=datetime.timezone.utc)),
        ),
    ]
