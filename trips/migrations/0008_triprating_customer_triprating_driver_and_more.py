# Generated by Django 4.2.4 on 2024-06-18 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin_api', '0006_feedbacksetting'),
        ('trips', '0007_trip_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='triprating',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cutomer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='triprating',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='driver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='triprating',
            name='feedbacksetting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='admin_api.feedbacksetting'),
        ),
    ]
