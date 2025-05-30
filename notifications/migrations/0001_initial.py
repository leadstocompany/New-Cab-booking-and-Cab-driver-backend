# Generated by Django 5.1.4 on 2025-02-02 18:48

import cloudinary.models
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DriverNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "banner",
                    cloudinary.models.CloudinaryField(
                        blank=True, max_length=255, null=True
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("url", models.URLField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
