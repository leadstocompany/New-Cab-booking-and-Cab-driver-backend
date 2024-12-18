# Generated by Django 4.2.4 on 2024-07-31 08:06

import cabs.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabs', '0023_alter_cabclass_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='back',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='back_head_light',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='front',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='front_head_light',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='inside_driver_seat',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='inside_passanger_seat',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='left',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='right',
        ),
        migrations.AddField(
            model_name='cabtype',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to=cabs.models.vehicle_type_directory_path),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_photo',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='vehiclemaker',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to=cabs.models.vehicle_maker_directory_path),
        ),
    ]