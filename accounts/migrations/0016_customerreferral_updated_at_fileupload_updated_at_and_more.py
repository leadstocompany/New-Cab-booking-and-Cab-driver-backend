# Generated by Django 4.2.4 on 2023-08-24 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_user_driver_duty'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerreferral',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='customerreferral',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
