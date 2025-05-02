from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from JLP_MyRide import settings
from admin_api.models import EmailTemplate
from trips.models import Trip
from utility.rating import get_driver_rating
from payment.models import Bill_Payment
from utility.fcm_notification import send_fcm_notification
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
import logging

from utility.util import get_bill_payment_mapping

logger = logging.getLogger(__name__)

@shared_task
def trip_bill_generate_task(trip_id):
    trip = Trip.objects.get(id=trip_id)
    channel_layer = get_channel_layer()
    group_name = f"payment_{trip.customer.id}"
    data= {
            "type": "send_trip_bille_notification",
            "message": f"You have a new payment request for your trip from {trip.source} to {trip.destination}.",
            "trip_id":str(trip.id),
            "source":trip.source,
            "destination":trip.destination,
            "pickup_latitude": trip.pickup_latitude,
            "pickup_longitude": trip.pickup_longitude,
            "drop_latitude": trip.drop_latitude,
            "drop_longitude": trip.drop_longitude,
            "time" :str(trip.time),
            "distance":str(trip.distance),
            "base_fare":float(trip.rent_price),
            "waiting_charge":float(trip.waiting_charge),
            "waiting_time":trip.waiting_time,
            "total_fare":float(trip.total_fare),
            "payment_type":trip.payment_type,
            "ride_type_id":trip.ride_type.id,
            "ride_type_name":trip.ride_type.cab_class,
            "driver_id":trip.driver.id,
            "driver_name":trip.driver.first_name + " " + trip.driver.last_name,
            "driver_phone":trip.driver.phone,
            "driver_photo":trip.driver.photo_upload,
            "driver_rating":str(get_driver_rating(trip.driver)),
        }

    async_to_sync(channel_layer.group_send)(
        group_name,
        data
        )
    


@shared_task
def trip_payment_complete_task(payment_id):
    payment=Bill_Payment.objects.get(id=payment_id)
    channel_layer = get_channel_layer()
    group_name = f"payment_{payment.passenger.id}"
    driver_data={
            "type": "send_trip_payment_complete",
            "trip_id":str(payment.trip.id),
            "source":payment.trip.source,
            "destination":payment.trip.destination,
            "pickup_latitude": payment.trip.pickup_latitude,
            "pickup_longitude": payment.trip.pickup_longitude,
            "drop_latitude":payment.trip.drop_latitude,
            "drop_longitude":payment.trip.drop_longitude,
            "driver_id":str(payment.driver.id),
            "driver_name":payment.driver.first_name + " " + payment.driver.last_name,
            "driver_phone":payment.driver.phone,
            "driver_photo":payment.driver.photo_upload,
            "driver_rating":str(get_driver_rating(payment.driver)),
            "amount":float(payment.amount),
            "currency":payment.currency,
            "payment_status":payment.payment_status,
            "payment_type":payment.payment_type
           
        }
    async_to_sync(channel_layer.group_send)(
        group_name,
        driver_data
        
    )

    passenger_data = {
            "type": "send_trip_payment_complete",
            "trip_id":str(payment.trip.id),
            "source":payment.trip.source,
            "destination":payment.trip.destination,
            "pickup_latitude": payment.trip.pickup_latitude,
            "pickup_longitude": payment.trip.pickup_longitude,
            "drop_latitude":payment.trip.drop_latitude,
            "drop_longitude":payment.trip.drop_longitude,
            "passenger_id":str(payment.passenger.id),
            "passenger_name":payment.passenger.first_name + " " + payment.passenger.last_name,
            "passenger_phone":payment.passenger.phone,
            "passenger_photo":payment.passenger.photo_upload,
            "amount":float(payment.amount),
            "currency":payment.currency,
            "payment_status":payment.payment_status,
            "payment_type":payment.payment_type
        }
    async_to_sync(channel_layer.group_send)(
        f"payment_{payment.driver.id}",
        passenger_data
        
    )


from django.template import Template, Context

@shared_task
def send_payment_confirmation_email(payment_id):
    
    
    payment, placeholder_mapping= get_bill_payment_mapping(payment_id)
    try:
        template = EmailTemplate.objects.get(is_active=True)
        template_obj = Template(template.html_content)
        context_obj = Context(placeholder_mapping) 
        html_message = template_obj.render(context_obj)
        subject = template.subject
    except EmailTemplate.DoesNotExist:
        html_message = render_to_string('emails/payment_confirmation.html', placeholder_mapping)
        subject = 'Payment Confirmation'

    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payment.passenger.email],
        html_message=html_message,
    )

