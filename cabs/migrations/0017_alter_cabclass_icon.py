# Generated by Django 4.2.4 on 2024-04-10 07:26

import cabs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabs', '0016_alter_vehiclemodel_model_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabclass',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to=cabs.models.vehicle_model_directory_path),
        ),
    ]
