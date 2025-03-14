# Generated by Django 4.2.4 on 2024-12-21 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReferralReward",
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
                ("title", models.CharField(blank=True, max_length=2000, null=True)),
                (
                    "referrer_reward_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=50.0,
                        help_text="Reward amount for the inviter (referrer).",
                        max_digits=10,
                    ),
                ),
                (
                    "referred_reward_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=25.0,
                        help_text="Reward amount for the invited (referred) customer.",
                        max_digits=10,
                    ),
                ),
            ],
            options={
                "db_table": "referral_reward",
            },
        ),
        migrations.CreateModel(
            name="CustomerReferral",
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
                (
                    "referrer_reward_amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "referred_reward_amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "referred",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="referrers",
                        to="accounts.customer",
                    ),
                ),
                (
                    "referrer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="referreds",
                        to="accounts.customer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Referral",
                "verbose_name_plural": "Customer Referrals",
                "db_table": "customer_referral",
                "unique_together": {("referrer", "referred")},
            },
        ),
    ]
