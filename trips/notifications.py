# notifications.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_driver(driver, trip):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'driver_{driver.id}',
        {
            'type': 'send_trip_request',
            'trip_id': trip.id,
            'source': trip.source,
            'destination': trip.destination,
            'ride_type': trip.ride_type.name,
        }
    )

def notify_trip_booked(customer, trip):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'customer_{customer.id}',
        {
            'type': 'send_trip_booked',
            'trip_id': trip.id,
            'driver': trip.driver.username,
            'source': trip.source,
            'destination': trip.destination,
        }
    )

def notify_trip_cancelled(driver, trip):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'driver_{driver.id}',
        {
            'type': 'send_trip_cancelled',
            'trip_id': trip.id,
        }
    )
