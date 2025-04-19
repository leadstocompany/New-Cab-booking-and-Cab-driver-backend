from trips.models import Trip
from utility.rating import get_driver_rating
from payment.models import Bill_Payment
from utility.fcm_notification import send_fcm_notification
import logging

from utility.util import get_notification_mapping, render_notification_template
logger = logging.getLogger(__name__)

def fcm_push_notification_trip_bill_generate(trip_id):
    trip = Trip.objects.get(id=trip_id)
    try:
        extra_mapping = {
            "PaymentAmount": trip.total_fare,
            "PaymentType": trip.payment_type,
        }
        mapping = get_notification_mapping(trip_id=trip_id, extra_mapping=extra_mapping)
        title, body = render_notification_template('TripBillGenerate', mapping)
        if title and body:
            response_data = send_fcm_notification(trip.customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip bill generate {trip.id}: {e}")

def fcm_push_notification_trip_payment_complete(payment_id):
    payment = Bill_Payment.objects.get(id=payment_id)
    mapping = get_notification_mapping(trip_id=payment.trip.id, payment_id=payment_id)

    try:
        title, body = render_notification_template('TripPaymentComplete', mapping)
        if title and body:
            response_data = send_fcm_notification(payment.passenger.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {payment.trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip payment complete {payment.trip.id}: {e}")

    try:
        title, body = render_notification_template('TripPaymentComplete', mapping)
        if title and body:
            response_data = send_fcm_notification(payment.driver.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {payment.trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip payment complete {payment.trip.id}: {e}")






