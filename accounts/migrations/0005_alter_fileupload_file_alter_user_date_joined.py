# Generated by Django 5.1.4 on 2025-02-17 10:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_date_joined_alter_user_photo_upload"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileupload",
            name="file",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 2, 17, 10, 56, 34, 577276, tzinfo=datetime.timezone.utc
                ),
                verbose_name="date joined",
            ),
        ),
    ]
