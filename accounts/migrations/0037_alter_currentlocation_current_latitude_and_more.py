# Generated by Django 4.2.4 on 2024-08-14 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_alter_bankaccount_bank_name_alter_bankaccount_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currentlocation',
            name='current_latitude',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='currentlocation',
            name='current_longitude',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
