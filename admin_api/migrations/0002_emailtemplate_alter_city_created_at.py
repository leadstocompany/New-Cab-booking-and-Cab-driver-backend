# Generated by Django 5.1.4 on 2025-04-14 05:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailTemplate",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("subject", models.CharField(max_length=255)),
                ("html_content", models.TextField()),
                ("is_active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Email Template",
                "verbose_name_plural": "Email Templates",
            },
        ),
        migrations.AlterField(
            model_name="city",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.localtime),
        ),
    ]
