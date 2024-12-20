# Generated by Django 4.2.4 on 2024-08-12 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_user_profile_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='currentlocation',
            name='current_latitude',
            field=models.DecimalField(decimal_places=21, max_digits=50),
        ),
        migrations.AlterField(
            model_name='currentlocation',
            name='current_longitude',
            field=models.DecimalField(decimal_places=21, max_digits=50),
        ),
    ]
