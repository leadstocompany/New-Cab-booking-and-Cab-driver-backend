# tasks.py

from celery import shared_task
from .models import Trip
from .notifications import send_notification_to_driver, send_trip_booked_notification

@shared_task
def send_booking_request_notifications(trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        # Notify all nearby drivers (replace with actual logic)
        nearby_drivers = get_nearby_drivers(trip)
        for driver in nearby_drivers:
            send_notification_to_driver(driver, trip)
    except Trip.DoesNotExist:
        pass

@shared_task
def notify_other_drivers(trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        # Notify other drivers that the trip is no longer available (replace with actual logic)
        # For example, send a notification to all drivers except the booked one
        other_drivers = get_other_drivers(trip)
        for driver in other_drivers:
            send_trip_booked_notification(driver, trip)
    except Trip.DoesNotExist:
        pass
