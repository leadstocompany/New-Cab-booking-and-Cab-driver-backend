# Generated by Django 4.2.4 on 2024-10-04 13:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_alter_bankaccount_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 13, 59, 5, 469045, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='customerreferral',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 13, 59, 5, 469045, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 13, 59, 5, 469045, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 4, 13, 59, 5, 471040, tzinfo=datetime.timezone.utc), verbose_name='date joined'),
        ),
    ]
