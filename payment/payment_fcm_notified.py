
from trips.models import Trip
from utility.rating import get_driver_rating
from payment.models import Bill_Payment
from utility.fcm_notification import send_fcm_notification


def fcm_push_notification_trip_bill_generate(trip_id):
    trip = Trip.objects.get(id=trip_id)
    data= {
            "type": "send_trip_bille_notification",
            "message": f"You have a new payment request for your trip from {trip.source} to {trip.destination}.",
            "trip_id":str(trip.id),
            "source":trip.source,
            "destination":trip.destination,
            "time" :str(trip.time),
            "distance":str(trip.distance),
            "base_fare":str(trip.rent_price),
            "waiting_charge":str(trip.waiting_charge),
            "waiting_time":trip.waiting_time,
            "total_fare":str(trip.total_fare),
            "payment_type":trip.payment_type,
            "ride_type_id":trip.ride_type.id,
            "ride_type_name":trip.ride_type.cab_class,
            "driver_id":trip.driver.id,
            "driver_name":trip.driver.first_name + " " + trip.driver.last_name,
            "driver_phone":trip.driver.phone,
            "driver_photo":trip.driver.photo_upload,
            "driver_rating":str(get_driver_rating(trip.driver)),
        }
    try:
        title=f"You have a new payment request for your trip from {trip.source} to {trip.destination}.",
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your have to reached your destination `{trip.destination}`, Please pay your ride charge and end your ride"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body, data)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')




def fcm_push_notification_trip_payment_complete(payment_id):
    payment=Bill_Payment.objects.get(id=payment_id)
    driver_data={
            "type": "send_trip_payment_complete",
            "trip_id":str(payment.trip.id),
            "source":payment.trip.source,
            "destination":payment.trip.destination,
            "driver_id":str(payment.driver.id),
            "driver_name":payment.driver.first_name + " " + payment.driver.last_name,
            "driver_phone":payment.driver.phone,
            "driver_photo":payment.driver.photo_upload,
            "driver_rating":str(get_driver_rating(payment.driver)),
            "amount":str(payment.amount),
            "currency":payment.currency,
            "payment_status":payment.payment_status,
            "payment_type":payment.payment_type
           
        }
    
    passenger_data = {
            "type": "send_trip_payment_complete",
            "trip_id":str(payment.trip.id),
            "source":payment.trip.source,
            "destination":payment.trip.destination,
            "passenger_id":str(payment.passenger.id),
            "passenger_name":payment.passenger.first_name + " " + payment.passenger.last_name,
            "passenger_phone":payment.passenger.phone,
            "passenger_photo":payment.passenger.photo_upload,
            "amount":str(payment.amount),
            "currency":payment.currency,
            "payment_status":payment.payment_status,
            "payment_type":payment.payment_type
        }
  
    try:
        title=f"Hello {payment.passenger.first_name}  {payment.passenger.last_name} , you have to paid for a ride."
        body=f"Hello {payment.passenger.first_name}  {payment.passenger.last_name}, you have to paid for a ride from {payment.trip.source} to {payment.trip.destination} and payment successfuly complated"
        # fcm_token="emXRnINNTZiEQb-Qklwn-I:APA91bFEf8KppgH-lEM15BLQSMA5uVMpooiw4kK42MF3Fy6kg_O8cwS4tj5grR9WvSCvjMFE0LcdDzcAygrjJ_8oEpcmNnXavU7yM-68ypBRdkHT5nLUPglozvw30u3BYSUrp7OnS515"
        response_data=send_fcm_notification(payment.passenger.fcm_token, title, body, driver_data)
        print(f'FCM notification {payment.trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {payment.trip.id}: {e}')

    
    try:
        title=f"Hello {payment.driver.first_name}  {payment.driver.last_name} , you have to paid for a ride."
        body=f"Hello {payment.driver.first_name}  {payment.driver.last_name}, you have to receive your ride payment for a ride from {payment.trip.source} to {payment.trip.destination} and payment reveived successfuly "
        response_data=send_fcm_notification(payment.driver.fcm_token, title, body, passenger_data)
        print(f'FCM notification {payment.trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {payment.trip.id}: {e}')






