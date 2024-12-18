
from trips.models import Trip
from utility.rating import get_driver_rating
from payment.models import Bill_Payment
from utility.fcm_notification import send_fcm_notification
import logging
logger = logging.getLogger(__name__)

def fcm_push_notification_trip_bill_generate(trip_id):
    trip = Trip.objects.get(id=trip_id)
    try:
        title=f"You have a new payment request for your trip from {trip.source} to {trip.destination}.",
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your have to reached your destination `{trip.destination}`, Please pay your ride charge and end your ride"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body)
        print(f'FCM notification {trip.id}: {response_data}')
        logger.debug(f"Processing data FCM notification: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred sending fcm notification for trip bill generate {trip.id}: {e}")
        print(f'Error sending fcm notification for trip bill generate {trip.id}: {e}')




def fcm_push_notification_trip_payment_complete(payment_id):
    payment=Bill_Payment.objects.get(id=payment_id)
    try:
        title=f"Hello {payment.passenger.first_name}  {payment.passenger.last_name} , you have to paid for a ride."
        body=f"Hello {payment.passenger.first_name}  {payment.passenger.last_name}, you have to paid for a ride from {payment.trip.source} to {payment.trip.destination} and payment successfuly complated"
        # fcm_token="emXRnINNTZiEQb-Qklwn-I:APA91bFEf8KppgH-lEM15BLQSMA5uVMpooiw4kK42MF3Fy6kg_O8cwS4tj5grR9WvSCvjMFE0LcdDzcAygrjJ_8oEpcmNnXavU7yM-68ypBRdkHT5nLUPglozvw30u3BYSUrp7OnS515"
        response_data=send_fcm_notification(payment.passenger.fcm_token, title, body)
        print(f'FCM notification {payment.trip.id}: {response_data}')
        logger.debug(f"Processing data FCM notification: {response_data}")
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {payment.trip.id}: {e}')
        logger.error(f"Error occurred sending fcm notification for trip cancel {payment.trip.id}: {e}")

    
    try:
        title=f"Hello {payment.driver.first_name}  {payment.driver.last_name} , you have paid for a ride."
        body=f"Hello {payment.driver.first_name}  {payment.driver.last_name}, you have to receive your ride payment for a ride from {payment.trip.source} to {payment.trip.destination} and payment reveived successfuly "
        response_data=send_fcm_notification(payment.driver.fcm_token, title, body)
        print(f'FCM notification {payment.trip.id}: {response_data}')
        logger.debug(f"Processing data FCM notification: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred sending fcm notification for trip cancel {payment.trip.id}: {e}")
        print(f'Error sending fcm notification for trip cancel {payment.trip.id}: {e}')






