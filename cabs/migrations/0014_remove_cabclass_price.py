# Generated by Django 4.2.4 on 2023-10-05 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabs', '0013_cabclass_icon_cabclass_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cabclass',
            name='price',
        ),
    ]
