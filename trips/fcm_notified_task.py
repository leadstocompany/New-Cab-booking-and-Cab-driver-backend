from trips.models import Trip
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
import requests
from apscheduler.schedulers.background import BackgroundScheduler


def fcm_push_notification_trip_booking_request_to_drivers(trip_id,drivers, scheduled_datetime):
    try:
        trip = Trip.objects.get(id=trip_id)
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
            'rent_price':str(trip.rent_price),
            'passenger_name':trip.customer.first_name + " " + trip.customer.last_name,
            "passenger_phone": trip.customer.phone,
            "passenger_photo":trip.customer.photo_upload
            }
        for driver in drivers:
            try:
                title=f"New Ride request comming"
                body=f"New ride request comming form {trip.source} to {trip.destination} and ride charge {float(trip.rent_price)}"
                response_data=send_fcm_notification(driver.fcm_token, title, body, trip_data)
                print(f'FCM notification {trip.id}: {response_data}')
            except Exception as e:
                print(f'Error sending fcm notification for trip request {trip.id}: {e}')
    except Exception as e:
        print("trip data error :", str(e))


def fcm_push_notification_trip_accepted(trip_id):
    trip = Trip.objects.get(id=trip_id)
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
        'rent_price':str(trip.rent_price),
        'driver_id':str(trip.driver.id),
        'driver_name': trip.driver.first_name + " " + trip.driver.last_name,
        'driver_phone': trip.driver.phone,
        'driver_photo':trip.driver.photo_upload,
        'driver_rating':str(get_driver_rating(trip.driver))
        }
 
    try:
        title=f"Driver Accept your ride request"
        body=f"Driver {trip.driver.first_name} {trip.driver.last_name} accept your ride request form {trip.source} to {trip.destination} and Driver will be reach your current location very soon"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body, trip_data)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
            print(f'Error sending fcm notification for trip booked {trip.id}: {e}')





def fcm_push_notification_trip_cancelled(trip_id,user_type, cancel_reason):
    trip = Trip.objects.get(id=trip_id)
   
    if user_type == 'driver':
        trip_data={
        'type': 'send_trip_cancelled',
        'trip_id': str(trip.id),
        'reason': cancel_reason,
        'cancel_by':"Passenger",
        'vehicle_id':str(trip.cab.id),
        'passenger_id':str(trip.customer.id),
        'passenger_name': trip.customer.first_name + " " + trip.customer.last_name,
        'passenger_phone':str(trip.customer.phone),
        'passenger_photo':trip.customer.photo_upload,
        }
     
        try:
            title=f"Passenger {trip.customer.first_name}  {trip.customer.last_name} canceled the ride"
            body=f"Passenger {trip.customer.first_name}  {trip.customer.last_name} canceled the ride for {trip.cancel_reason}"
            response_data=send_fcm_notification(trip.driver.fcm_token, title, body, trip_data)
            print(f'FCM notification {trip.id}: {response_data}')
        except Exception as e:
            print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
    elif user_type == 'customer':
        trip_data={
            'type': 'send_trip_cancelled',
            'trip_id': str(trip.id),
            'reason': cancel_reason,
            'cancel_by':"Passenger",
            'driver_id':str(trip.driver.id),
            'driver_name':trip.driver.first_name + " " + trip.driver.last_name,
            "driver_phone": trip.driver.phone,
            "driver_photo":trip.driver.photo_upload,
            'driver_rating':str(get_driver_rating(trip.driver)),
            'vehicle_id':str(trip.cab.id), 
            'vehicle_number':trip.cab.number_plate, 
            }
      
        try:
            title=f"Driver {trip.driver.first_name}  {trip.driver.last_name} canceled the ride"
            body=f"Driver {trip.driver.first_name}  {trip.driver.last_name} canceled the ride for {trip.cancel_reason}"
            response_data=send_fcm_notification(trip.customer.fcm_token, title, body, trip_data)
            print(f'FCM notification {trip.id}: {response_data}')
        except Exception as e:
            print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')





def fcm_push_notification_trip_started(trip_id):
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

    try:
        title=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride start now"
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride start now form {trip.source} to {trip.destination}"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body, trip_data)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')






def fcm_push_notification_trip_completed(trip_id, customer_id, driver_id):
  
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
    
    try:
        title=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride completed"
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your have to reached your destination `{trip.destination}` and your ride has been complated"
        response_data=send_fcm_notification(customer.fcm_token, title, body, trip_data)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')


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
    try:
        title=f"Hello {trip.driver.first_name}  {trip.driver.last_name}, Your ride completed"
        body=f"Hello {trip.driver.first_name}  {trip.driver.last_name}, Your have to reached your destination `{trip.destination}` and your ride has been complated"
        response_data=send_fcm_notification(driver.fcm_token, title, body, trip_data1)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')




def fcm_push_notification_arrived_at_pickup(trip_id, customer_id, driver_id):
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
   
    try:
        title=f"Hello {customer.first_name}  {customer.last_name}, Your ride driver have reached near you"
        body=f"Hello {customer.first_name}  {customer.last_name}, Your ride driver {driver.first_name} {driver.last_name} have reached near you, please contact with your rider throught of the number are {driver.phone}"
        fcm_token="e0fCQ0pnTJ2olw-iBFbfqk:APA91bG5JGkzCBXFM03nEMiKp_XYu09JKSat4WZ6n7beWhGh-_M-4Ay1lCEL-cUFAIPvHEQl9YRFte--3fUcyS4--4I9fgGPx4DkqV5DbwtK1lXKGKtxjm38F5Sy-7KuPW1SVVwe6cgw"
       
        response_data=send_fcm_notification(customer.fcm_token, title, body, trip_data)
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')









def send_fcm_notification_schedule(trip_id):
    scheduler = BackgroundScheduler()
    trip = Trip.objects.get(id=trip_id) 
    if trip.scheduled_datetime and timezone.now() <=  trip.scheduled_datetime - timedelta(hours=1):
        schedule_time=trip.scheduled_datetime - timedelta(hours=1)
        scheduled_time_str = trip.scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')
        title=f'Your trip is scheduled to start at {scheduled_time_str}.'
        body=f"Your trip is scheduled to start at {scheduled_time_str}, from {trip.source} to {trip.destination} "
        if trip.customer:
            data={
                "trip_id":str(trip.id),
                "source":trip.source,
                "destination":trip.destination,
                "ride_type":trip.ride_type.cab_class,
                "driver_id":str(trip.driver.id),
                "driver_name":f"{trip.driver.first_name} {trip.driver.last_name}",
                "driver_phone":trip.driver.phone,
                "driver_photo":trip.driver.photo_upload,
                "vehicle_id":str(trip.cab.id),
                "vehicle_number":str(trip.cab.number_plate)
                }
            token=trip.customer.fcm_token
            scheduler.add_job(
                send_fcm_notification,
                'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                run_date=schedule_time,  # Time to send the notification
                args=[token, title, body,data]  # Arguments for the functio
                )
            # Start the scheduler
            scheduler.start()
        if trip.driver:
            trip_data={
                "trip_id":str(trip.id),
                "source":trip.source,
                "destination":trip.destination,
                "ride_type":trip.ride_type.cab_class,
                "ride_charge":str(trip.rent_price),
                "passenger_id":str(trip.customer.id),
                "passenger_name":f"{trip.customer.first_name} {trip.customer.last_name}",
                "passenger_phone":trip.customer.phone,
                "passenger_photo":trip.customer.photo_upload,
                }
            driver_fcm_token=trip.driver.fcm_token
            scheduler.add_job(
                send_fcm_notification,
                'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                run_date=schedule_time,  # Time to send the notification
                args=[driver_fcm_token, title, body,trip_data]  # Arguments for the functio
                )
            # Start the scheduler
            scheduler.start()
           






