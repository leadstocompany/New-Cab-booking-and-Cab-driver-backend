# tasks.py
# tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trips.models import Trip
from trips.notifications import notify_driver, notify_trip_booked, notify_trip_cancelled, send_real_time_notification
from django.db.models import Q
from accounts.models import User, CurrentLocation
from subscriptions.models import Subscription
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail


@shared_task
def notify_drivers(trip_id, latitude, longitude,scheduled_datetime):
   
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
            subscription = Subscription.objects.filter(driver=driver, is_active=True).first()
            if subscription and subscription.pending_rides > 0:
                location = driver.currentlocation
                distance = haversine(float(latitude), float(longitude), location.current_latitude, location.current_longitude)
                if distance <= max_distance:
                    nearby_drivers.append(driver)
        except CurrentLocation.DoesNotExist:
            continue

    # Notify drivers
    for driver in nearby_drivers:
        notify_driver(driver, trip, scheduled_datetime)

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



@shared_task
def notify_trip_cancelled(trip_id, user_id, user_type):
    trip = Trip.objects.get(id=trip_id)
    channel_layer = get_channel_layer()
    message = {
        'type': 'send_trip_cancelled',
        'message': {
            'trip_id': trip.id,
            'reason': 'Trip has been cancelled by the other party.',
        }
    }
    if user_type == 'driver':
        async_to_sync(channel_layer.group_send)(f'driver_{user_id}', message)
    elif user_type == 'customer':
        async_to_sync(channel_layer.group_send)(f'customer_{user_id}', message)




@shared_task
def notify_trip_started(trip_id, customer_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{customer_id}",
        {
            "type": "trip_started",
            "message": f"Your trip with ID {trip_id} has started.",
        }
    )




@shared_task
def notify_trip_completed(trip_id, customer_id, driver_id):
    channel_layer = get_channel_layer()
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)

    # Notify customer
    async_to_sync(channel_layer.group_send)(
        f"customer_{customer.id}",
        {
            "type": "trip.completed",
            "message": f"Your trip from {trip.source} to {trip.destination} has been completed.",
            "trip_id": trip.id
        }
    )

    # Notify driver
    async_to_sync(channel_layer.group_send)(
        f"driver_{driver.id}",
        {
            "type": "trip.completed",
            "message": f"Your trip from {trip.source} to {trip.destination} has been completed.",
            "trip_id": trip.id
        }
    )




@shared_task
def send_trip_notification(trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        if trip.scheduled_time and timezone.now() <= trip.scheduled_time - timedelta(hours=1):
            # customer_email = trip.customer.email
            # driver_email = trip.driver.email if trip.driver else None

            scheduled_time_str = trip.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')

            # # Sending email notifications (you can replace this with your notification system)
            # send_mail(
            #     'Trip Reminder',
            #     f'Your trip from {trip.source} to {trip.destination} is scheduled to start at {scheduled_time_str}.',
            #     'from@example.com',
            #     [customer_email, driver_email],
            #     fail_silently=False,
            # )

            # Send real-time notifications via Django Channels (assumed implemented)
            send_real_time_notification(trip.customer, f'Your trip is scheduled to start at {scheduled_time_str}.')
            if trip.driver:
                send_real_time_notification(trip.driver, f'Your trip is scheduled to start at {scheduled_time_str}.')
    except Trip.DoesNotExist:
        pass


@shared_task
def payment_request_notified(trip):
    channel_layer = get_channel_layer()
    group_name = f"user_{trip.customer.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_payment_request_notification",
            "message": f"You have a new payment request for your trip from {trip.source} to {trip.destination}.",
            "trip_id":trip.id,
            "source":trip.source,
            "destination":trip.destination,
            "time" :trip.time,
            "distance":trip.distance,
            "waiting_charge":trip.waiting_charge,
            "waiting_time":trip.waiting_time,
            "total_fare":trip.total_fare,
            "payment_type":trip.payment_type,
        }
    )
