# Generated by Django 4.2.4 on 2024-08-25 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0037_alter_currentlocation_current_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]