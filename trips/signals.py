# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from trips.models import Trip
from trips.tasks import send_trip_notification

@receiver(post_save, sender=Trip)
def schedule_trip_notification(sender, instance, created, **kwargs):
    if created and instance.scheduled_datetime:
        send_trip_notification.apply_async(
            (instance.id,),
            eta=instance.scheduled_datetime - timedelta(hours=1)
        )
