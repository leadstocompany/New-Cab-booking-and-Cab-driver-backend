# Generated by Django 4.2.4 on 2024-07-24 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0006_feedbacksetting'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdocumentfield',
            old_name='frontback',
            new_name='back',
        ),
        migrations.AddField(
            model_name='userdocumentfield',
            name='front',
            field=models.BooleanField(default=True),
        ),
    ]
