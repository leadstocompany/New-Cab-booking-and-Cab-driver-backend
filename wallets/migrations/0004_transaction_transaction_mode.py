# Generated by Django 4.2.4 on 2024-09-30 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0003_rename_remake_transaction_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_mode',
            field=models.CharField(blank=True, choices=[('WALLETS', 'Wallets'), ('HANDCASH', 'HandCash'), ('STRIPEPAY', 'StripePay')], max_length=80, null=True),
        ),
    ]
