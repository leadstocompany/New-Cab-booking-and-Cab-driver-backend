# Generated by Django 4.2.4 on 2024-06-26 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_rename_user_doccument_user_user_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_document',
            new_name='user_doc',
        ),
    ]
