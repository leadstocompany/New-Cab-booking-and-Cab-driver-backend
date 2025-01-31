# tasks.py
# tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trips.fcm_notified_task import fcm_push_notification_trip_booking_request_to_drivers
from trips.models import Trip
from trips.notifications import booking_request_notify_driver, notify_trip_booked, send_real_time_notification, notify_trip_request_cancel
# notify_trip_booking_closed,
from django.db.models import Q
from accounts.models import User, CurrentLocation
from subscriptions.models import Subscriptions
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from decimal import Decimal
from datetime import datetime, timedelta
from utility.rating import get_driver_rating
from utility.fcm_notification import send_fcm_notification
from accounts.models import Driver
import requests
import logging
from trips.models import Trip
from utility.nearest_driver_list import get_nearest_driver_list


logger = logging.getLogger(__name__)

# @shared_task
# def booking_request_notify_drivers(trip_id, latitude, longitude,scheduled_datetime):
#     try:
#         trip = Trip.objects.get(id=trip_id)
#         max_distance = 5.0  # This could be made dynamic
#         radius = 6371  # Earth's radius in kilometers

#         def haversine(lat1, lon1, lat2, lon2):
#             import math
#             lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#             dlat = lat2 - lat1
#             dlon = lon2 - lon1
#             a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
#             c = 2 * math.asin(math.sqrt(a))
#             return radius * c

#         active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
#         drivers_without_active_trips = User.objects.filter(
#             type=User.Types.DRIVER, driver_duty=True
#         ).exclude(
#             Q(driver_trips__status__in=active_trip_statuses)
#         ).distinct()
#         print(trip.ride_type)
#         if trip.ride_type_id:
          
#             drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=trip.ride_type_id)

#         nearby_drivers = []

#         for driver in drivers_without_active_trips:
#             try:
#                 subscription = Subscriptions.objects.filter(driver=driver, is_active=True, payment_status="PAID").first()
#                 # if subscription and subscription.pending_rides > 0:
#                 if subscription:
                    
#                     if not subscription.is_expired():
#                         location = driver.currentlocation
#                         distance = haversine(float(latitude), float(longitude), float(location.current_latitude), float(location.current_longitude))
#                         if distance <= max_distance:
#                             nearby_drivers.append(driver)
                    
#             except CurrentLocation.DoesNotExist:
#                 continue
#         # Notify drivers
#         for driver in nearby_drivers:
#             print("yes")
#             booking_request_notify_driver(driver, trip, scheduled_datetime)
#     except Exception as e:
#         print("celery error :", e)


@shared_task
def booking_request_notify_drivers(trip_id,driver_ids, scheduled_datetime):
    try:
        trip = Trip.objects.get(id=trip_id)
        # Notify drivers
        drivers=Driver.objects.filter(id__in=driver_ids)
        for driver in drivers:
            print("yes")
            booking_request_notify_driver(driver, trip, scheduled_datetime)
    except Exception as e:
        logger.error(f"Celery Error occurred: {e}")
        print("celery error :", e)

@shared_task
def schedule_driver_notifications(trip_id, pickup_latitude, pickup_longitude, scheduled_datetime):
    trip = Trip.objects.get(id=trip_id)
    
    # Get nearest drivers at notification time
    drivers=get_nearest_driver_list(trip.id, pickup_latitude, pickup_longitude)
    driver_ids = [driver.id for driver in drivers]
    fcm_push_notification_trip_booking_request_to_drivers(trip.id,drivers, scheduled_datetime)
    booking_request_notify_drivers.delay(trip.id,driver_ids, scheduled_datetime)


@shared_task
def notify_trip_accepted(trip_id):
    trip = Trip.objects.get(id=trip_id)
    # Notify the customer
    notify_trip_booked(trip.customer, trip)

    # Notify other drivers that the trip has been booked
    # other_drivers = trip.driver_trips.filter(status='REQUESTED').exclude(driver=driver)
    # for other_driver in other_drivers:
    #     notify_trip_booking_closed(other_driver, trip)

@shared_task
def notify_trip_request_cancel(trip_id, driver_ids, cancel_reason):
    trip = Trip.objects.get(id=trip_id)
    trip_data={
        'type': 'send_trip_cancelled',
        'trip_id': str(trip.id),
        'reason': cancel_reason,
        'cancel_by':"Passenger",
        'passenger_id':str(trip.customer.id),
        'passenger_name': trip.customer.first_name + " " + trip.customer.last_name,
        'passenger_phone':str(trip.customer.phone),
        'passenger_photo':trip.customer.photo_upload,
        }
    for driver_id in driver_ids:
        notify_trip_request_cancel(driver_id, trip_data)
    
   

@shared_task
def notify_trip_cancelled(trip_id, user_id, user_type, cancel_reason):
    trip = Trip.objects.get(id=trip_id)
    channel_layer = get_channel_layer()
    
    if user_type == 'driver':
        trip_data={
        'trip_id': str(trip.id),
        'reason': cancel_reason,
        'cancel_by':"Passenger",
        'vehicle_id':str(trip.cab.id),
        'passenger_id':str(trip.customer.id),
        'passenger_name': trip.customer.first_name + " " + trip.customer.last_name,
        'passenger_phone':str(trip.customer.phone),
        'passenger_photo':trip.customer.photo_upload,
        }
        message = {
        'type': 'send_trip_cancelled',
        'message': trip_data
        }
        async_to_sync(channel_layer.group_send)(f'driver_{user_id}', message)
       
    elif user_type == 'customer':
        trip_data={
            'trip_id': str(trip.id),
            'reason': cancel_reason,
            'cancel_by':"Passenger",
            'driver_id':str(trip.driver.id),
            'driver_name':trip.driver.first_name + " " + trip.driver.last_name,
            "driver_phone": trip.driver.phone,
            "driver_photo":trip.driver.photo_upload,
            'driver_rating':str(get_driver_rating(trip.driver)),
            'vehicle_id':str(trip.cab.id),   
            }
        message = {
        'type': 'send_trip_cancelled',
        'message': trip_data
        }
        async_to_sync(channel_layer.group_send)(f'customer_{user_id}', message)
      



@shared_task
def notify_trip_started(trip_id):
    trip = Trip.objects.get(id=trip_id)
    trip_data = {
        "type": "trip_started",
        "trip_id":str(trip.id),
        'source': trip.source,
        'destination': trip.destination,
        'ride_type': trip.ride_type.cab_class,
        'vehicle_id':str(trip.cab.id),
        'driver_id':str(trip.driver.id),
        'driver_name':trip.driver.first_name + " " + trip.driver.last_name,
        "driver_phone": trip.driver.phone,
        "driver_photo":trip.driver.photo_upload,
        "driver_rating":str(get_driver_rating(trip.driver)),
        "message": f"Your trip with ID {trip.id} has started from {trip.source} to {trip.destination}.",
        }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"customer_{trip.customer.id}",
        trip_data
    )



@shared_task
def notify_trip_completed(trip_id, customer_id, driver_id):
    channel_layer = get_channel_layer()
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    # Notify customer and driver
    trip_data= {
        "type": "trip_completed",
        "message": f"Your trip from {trip.source} to {trip.destination} has been completed.",
        "trip_id": str(trip.id),
        'driver_id':str(trip.driver.id),
        'driver_name':trip.driver.first_name + " " + trip.driver.last_name,
        "driver_phone": trip.driver.phone,
        "driver_photo":trip.driver.photo_upload,
        "driver_rating":str(get_driver_rating(trip.driver)),
    }
    async_to_sync(channel_layer.group_send)(
        f"customer_{customer.id}",
        trip_data   
    )



    # # Notify driver
    trip_data1={
            "type": "trip_completed",
            "message": f"Your trip from {trip.source} to {trip.destination} has been completed.",
            "trip_id": str(trip.id),
            'passenger_id':str(trip.customer.id),
            'passenger_name':trip.customer.first_name + " " + trip.driver.last_name,
            "passenger_phone": trip.customer.phone,
            "passenger_photo":trip.customer.photo_upload,
            # "driver_rating":get_driver_rating(trip.driver),
        }
  
    async_to_sync(channel_layer.group_send)(
        f"driver_{driver.id}",
        trip_data1
    )

    



@shared_task
def send_trip_schedule_notification(trip_id):
    try:
        trip = Trip.objects.get(id=trip_id) 
        # scheduled_datetime = datetime.strptime(trip.scheduled_datetime, '%Y-%m-%d %H:%M:%S')

        if trip.scheduled_datetime and timezone.now() <=  trip.scheduled_datetime - timedelta(hours=1):
            # customer_email = trip.customer.email
            # driver_email = trip.driver.email if trip.driver else None

            scheduled_time_str = trip.scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')
            # Send real-time notifications via Django Channels (assumed implemented)
            send_real_time_notification(f'customer_{trip.customer.id}', f'Your trip is scheduled to start at {scheduled_time_str}.', trip.id, trip.source,
            trip.destination,trip.ride_type.cab_class, scheduled_time_str)
            
            if trip.driver:
                send_real_time_notification(f'driver_{trip.driver.id}', f'Your trip is scheduled to start at {scheduled_time_str}.', trip.id, trip.source, trip.destination,trip.ride_type.cab_class,scheduled_time_str)    
    except Trip.DoesNotExist as e:
        logger.error(f"Celery Error occurred: {e}")
        pass





@shared_task
def notify_arrived_at_pickup(trip_id, customer_id, driver_id):
    channel_layer = get_channel_layer()
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    # Notify customer and driver
    trip_data= {
        "type": "arrived_at_pickup",
        "message": f"Your driver have reached near you",
        "trip_id": str(trip.id),
        'driver_id':str(trip.driver.id),
        'driver_name':trip.driver.first_name + " " + trip.driver.last_name,
        "driver_phone": trip.driver.phone,
        "driver_photo":trip.driver.photo_upload,
        "driver_rating":str(get_driver_rating(trip.driver)),
        "vehicle_id":str(trip.cab.id),
        "vehicle_number":str(trip.cab.number_plate)
    }
    async_to_sync(channel_layer.group_send)(
        f"customer_{customer.id}",
        trip_data   
    )
  