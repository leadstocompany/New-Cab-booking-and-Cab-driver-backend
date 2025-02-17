# Generated by Django 5.1.4 on 2025-02-16 20:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_fileupload_file_alter_user_date_joined_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.CharField(blank=True, max_length=274, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="country",
            field=models.CharField(blank=True, max_length=74, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="landmark",
            field=models.CharField(blank=True, max_length=274, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 16, 20, 13, 56, 462179, tzinfo=datetime.timezone.utc
                ),
                verbose_name="date joined",
            ),
        ),
    ]
