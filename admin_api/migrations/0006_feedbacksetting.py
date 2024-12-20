# Generated by Django 4.2.4 on 2024-06-18 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0005_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('sub_title', models.CharField(blank=True, max_length=500, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
