# signals.py
# from datetime import datetime, timedelta
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from datetime import timedelta
# from trips.models import Trip
# from trips.tasks import send_trip_schedule_notification

# @receiver(post_save, sender=Trip)
# def schedule_trip_notification(sender, instance, created, **kwargs):
#     if created and instance.scheduled_datetime:
#         scheduled_datetime = datetime.strptime(instance.scheduled_datetime, '%Y-%m-%d %H:%M:%S')
#         send_trip_schedule_notification.apply_async(
#             (instance.id,),
#             eta=scheduled_datetime - timedelta(hours=1)
#         )

       









 