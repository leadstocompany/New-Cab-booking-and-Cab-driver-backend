# Generated by Django 5.1.4 on 2025-02-17 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cabs", "0003_alter_cabclass_icon_alter_cabtype_icon_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cabclass",
            name="icon",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="cabtype",
            name="icon",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="vehiclemaker",
            name="icon",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="vehiclemodel",
            name="model_image",
            field=models.CharField(blank=True, null=True),
        ),
    ]
