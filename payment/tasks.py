from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trips.models import Trip



@shared_task
def trip_bill_generate_task(trip_id):
    trip = Trip.objects.get(id=trip_id)
    channel_layer = get_channel_layer()
    group_name = f"payment_{trip.customer.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_trip_bille_notification",
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
