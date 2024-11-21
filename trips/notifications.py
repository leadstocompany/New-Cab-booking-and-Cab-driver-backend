# notifications.py

from utility.rating import get_driver_rating
from utility.fcm_notification import send_fcm_notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def booking_request_notify_driver(driver, trip, scheduled_datetime):
    try:
        trip_data={
            'type': 'send_trip_request',
            'trip_id': str(trip.id),
            'source': trip.source,
            'destination': trip.destination,
            'ride_type': trip.ride_type.cab_class,
            'scheduled_datetime':str(scheduled_datetime),
            'payment_type':trip.payment_type,
            'pickup_latitude':str(trip.pickup_latitude),
            'pickup_longitude':str(trip.pickup_longitude),
            'dropup_latitude':str(trip.dropup_latitude),
            'dropup_longitude':str(trip.dropup_longitude),
            'rent_price':float(trip.rent_price),
            'passenger_name':trip.customer.first_name + " " + trip.customer.last_name,
            "passenger_phone": trip.customer.phone,
            "passenger_photo":trip.customer.photo_upload
            }
        try:
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f'driver_{driver.id}',
                trip_data
            )
            print(f'Notification successfully sent for trip {trip.id}')
        except Exception as e:
             print(f'Error sending notification for trip {trip.id}: {e}')
    except Exception as e:
         print(f'Error sending notification for trip {trip.id}: {e}')


def notify_trip_booked(customer, trip):
    trip_data={
        'type': 'send_trip_booked',
        'trip_id': str(trip.id),
        'source': trip.source,
        'destination': trip.destination,
        'ride_type': trip.ride_type.cab_class,
        'vehicle_id':str(trip.cab.id),
        'scheduled_datetime':str(trip.scheduled_datetime),
        'payment_type':trip.payment_type,
        'pickup_latitude':str(trip.pickup_latitude),
        'pickup_longitude':str(trip.pickup_longitude),
        'dropup_latitude':str(trip.dropup_latitude),
        'dropup_longitude':str(trip.dropup_longitude),
        'rent_price':float(trip.rent_price),
        'driver_id':str(trip.driver.id),
        'driver_name': trip.driver.first_name + " " + trip.driver.last_name,
        'driver_phone': trip.driver.phone,
        'driver_photo':trip.driver.photo_upload,
        'driver_rating':str(get_driver_rating(trip.driver))
        }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'customer_{customer.id}',
        trip_data
       
    )
def notify_trip_request_cancel(driver_id, trip_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'driver_{driver_id}',
        trip_data
    )

# def notify_trip_booking_closed(driver, trip):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f'ride_booking_closed_{driver.id}',
#         {
#             'type': 'send_ride_booking_closed',
#             'trip_id': trip.id,
#             'source': trip.source,
#             'destination': trip.destination,
#             'ride_type': trip.ride_type.cab_class,
#             'massege':'Trip booking closed'
#         }
#     )



# def notify_trip_cancelled(driver, trip):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f'driver_{driver.id}',
#         {
#             'type': 'send_trip_cancelled',
#             'trip_id': trip.id,
#         }
#     )




def send_real_time_notification(group_name, message, trip_id, trip_source,trip_destination,ride_type,scheduled_time_str):
    trip_data={
        "type": "send_trip_schedule_notification",
        "message": message,
        'trip_id':trip_id,
        'source':trip_source,
        'destination':trip_destination,
        'ride_type':ride_type,
        'scheduled_time':scheduled_time_str,
        }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        trip_data
    )

    




   