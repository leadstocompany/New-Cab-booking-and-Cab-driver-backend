# Generated by Django 5.1.4 on 2025-02-02 16:26

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cabs", "0002_cabbookingprice_scheduled_trip_fare_precentage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cabclass",
            name="icon",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="cabtype",
            name="icon",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="vehiclemaker",
            name="icon",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="vehiclemodel",
            name="model_image",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True
            ),
        ),
    ]
