# Generated by Django 5.1.4 on 2025-04-14 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0003_alter_drivernotification_created_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationTemplate",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("email", "Email"),
                            ("sms", "SMS"),
                            ("push", "Push Notification"),
                        ],
                        max_length=50,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
