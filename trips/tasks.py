# tasks.py
# tasks.py

from celery import shared_task
from .models import Trip
from .notifications import notify_driver, notify_trip_booked, notify_trip_cancelled
from django.db.models import Q

@shared_task
def notify_drivers(trip_id, latitude, longitude):
    from .models import User, Trip, CurrentLocation
    trip = Trip.objects.get(id=trip_id)
    max_distance = 5.0  # This could be made dynamic
    radius = 6371  # Earth's radius in kilometers

    def haversine(lat1, lon1, lat2, lon2):
        import math
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return radius * c

    active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
    drivers_without_active_trips = User.objects.filter(
        type=User.Types.DRIVER, driver_duty=True
    ).exclude(
        Q(driver_trips__status__in=active_trip_statuses)
    ).distinct()

    if trip.ride_type_id:
        drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=trip.ride_type_id)

    nearby_drivers = []

    for driver in drivers_without_active_trips:
        try:
            location = driver.currentlocation
            distance = haversine(latitude, longitude, location.current_latitude, location.current_longitude)
            if distance <= max_distance:
                nearby_drivers.append(driver)
        except CurrentLocation.DoesNotExist:
            continue

    # Notify drivers
    for driver in nearby_drivers:
        notify_driver(driver, trip)

@shared_task
def notify_trip_accepted(trip_id, driver_id):
    trip = Trip.objects.get(id=trip_id)
    if trip.status != 'REQUESTED':
        return

    trip.driver_id = driver_id
    trip.status = 'BOOKED'
    trip.save()

    # Notify the customer
    notify_trip_booked(trip.customer, trip)

    # Notify other drivers that the trip has been booked
    other_drivers = trip.driver_trips.filter(status='REQUESTED').exclude(driver_id=driver_id)
    for other_driver in other_drivers:
        notify_trip_cancelled(other_driver, trip)





# from celery import shared_task
# from .models import Trip
# from .notifications import send_notification_to_driver, send_trip_booked_notification

# @shared_task
# def send_booking_request_notifications(trip_id):
#     try:
#         trip = Trip.objects.get(id=trip_id)
#         # Notify all nearby drivers (replace with actual logic)
#         nearby_drivers = get_nearby_drivers(trip)
#         for driver in nearby_drivers:
#             send_notification_to_driver(driver, trip)
#     except Trip.DoesNotExist:
#         pass

# @shared_task
# def notify_other_drivers(trip_id):
#     try:
#         trip = Trip.objects.get(id=trip_id)
#         # Notify other drivers that the trip is no longer available (replace with actual logic)
#         # For example, send a notification to all drivers except the booked one
#         other_drivers = get_other_drivers(trip)
#         for driver in other_drivers:
#             send_trip_booked_notification(driver, trip)
#     except Trip.DoesNotExist:
#         pass
