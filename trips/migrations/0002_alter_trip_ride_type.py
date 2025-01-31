# Generated by Django 5.1.4 on 2025-01-31 19:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cabs", "0001_initial"),
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trip",
            name="ride_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="cabs.cabclass",
            ),
        ),
    ]
