from celery import shared_task

from utility.fcm_notification import send_rich_fcm_notification
from utility.nearest_driver_list import get_all_available_drivers


@shared_task
def send_driver_notifications(notification_id):
    from notifications.models import DriverNotification

    notification = DriverNotification.objects.get(id=notification_id)
    drivers = get_all_available_drivers(return_object=True)
    print(drivers)

    for driver in drivers:
        if driver.fcm_token:
            send_rich_fcm_notification(
                driver.fcm_token,
                notification.title,
                notification.message,
                notification.banner,
                notification.url,
            )
