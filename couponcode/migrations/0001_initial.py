# Generated by Django 4.2.4 on 2024-12-21 16:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
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
                ("name", models.CharField(blank=True, max_length=1000, null=True)),
                ("title", models.CharField(blank=True, max_length=1000, null=True)),
                ("terms_conditions", models.TextField(blank=True, null=True)),
                ("code", models.CharField(editable=False, max_length=10, unique=True)),
                ("discount", models.DecimalField(decimal_places=2, max_digits=5)),
                ("valid_from", models.DateTimeField()),
                ("valid_to", models.DateTimeField()),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="CouponUsage",
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
                ("used_at", models.DateTimeField(auto_now_add=True)),
                (
                    "coupon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="couponcode.coupon",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "couponusage",
                "unique_together": {("user", "coupon")},
            },
        ),
    ]
