from cabs.models import CabBookingPrice, Vehicle
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
import logging
logger = logging.getLogger(__name__)

def fcm_push_notification_trip_booking_request_to_drivers(trip_id,drivers, scheduled_datetime):
    try:
        trip = Trip.objects.get(id=trip_id)
       
        for driver in drivers:
            try:
                cab_custom_price = trip.rent_price
                
                if trip.ride_type is None or trip.total_fare is None:
                    vehicle = Vehicle.objects.get(driver_id=driver.id)
                    cabclass_value = CabBookingPrice.objects.get(cab_class_id=vehicle.cab_class.id)
                    cab_custom_price = cabclass_value.base_fare * trip.distance
                title=f"New Ride request comming"
                body=f"New ride request comming form {trip.source} to {trip.destination} and ride charge {float(cab_custom_price)}"
                print(driver.fcm_token, 'token')
                response_data=send_fcm_notification(driver.fcm_token, title, body)
                logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
                print(f'FCM notification {trip.id}: {response_data}')
            except Exception as e:
                logger.error(f"Error occurred in sending fcm notification for trip request {trip.id}: {e}")
                print(f'Error sending fcm notification for trip request {trip.id}: {e}')
    except Exception as e:
        print("trip data error :", str(e))
        logger.error(f"trip request {trip.id}: {e}")


def fcm_push_notification_trip_accepted(trip_id):
    trip = Trip.objects.get(id=trip_id)
    try:
        title=f"Driver Accept your ride request"
        body=f"Driver {trip.driver.first_name} {trip.driver.last_name} accept your ride request form {trip.source} to {trip.destination} and Driver will be reach your current location very soon"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body)
        print(f'FCM notification {trip.id}: {response_data}')
        logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending fcm notification for trip booked {trip.id}: {e}")





def fcm_push_notification_trip_cancelled(trip_id,user_type, cancel_reason):
    trip = Trip.objects.get(id=trip_id)
   
    if user_type == 'driver':
        try:
            title=f"Passenger {trip.customer.first_name}  {trip.customer.last_name} canceled the ride"
            body=f"Passenger {trip.customer.first_name}  {trip.customer.last_name} canceled the ride for {trip.cancel_reason}"
            response_data=send_fcm_notification(trip.driver.fcm_token, title, body)
            print(f'FCM notification {trip.id}: {response_data}')
        except Exception as e:
            print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
            logger.error(f"Error occurred in sending fcm notification for trip cancel {trip.id}: {e}'")
    elif user_type == 'customer':  
        try:
            title=f"Driver {trip.driver.first_name}  {trip.driver.last_name} canceled the ride"
            body=f"Driver {trip.driver.first_name}  {trip.driver.last_name} canceled the ride for {trip.cancel_reason}"
            response_data=send_fcm_notification(trip.customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
            print(f'FCM notification {trip.id}: {response_data}')
        except Exception as e:
            print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
            logger.error(f"Error occurred in sending fcm notification for trip  cancel by driver {trip.id}: {e}'")





def fcm_push_notification_trip_started(trip_id):
    trip = Trip.objects.get(id=trip_id)
   
    try:
        title=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride start now"
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride start now form {trip.source} to {trip.destination}"
        response_data=send_fcm_notification(trip.customer.fcm_token, title, body)
        logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
        print(f'FCM notification {trip.id}: {response_data}')
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
        logger.error(f"Error occurred in sending fcm notification for trip  start {trip.id}: {e}'")






def fcm_push_notification_trip_completed(trip_id, customer_id, driver_id):
  
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    # Notify customer and driver
    try:
        title=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your ride completed"
        body=f"Hello {trip.customer.first_name}  {trip.customer.last_name}, Your have to reached your destination `{trip.destination}` and your ride has been complated"
        response_data=send_fcm_notification(customer.fcm_token, title, body)
        print(f'FCM notification {trip.id}: {response_data}')
        logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
        logger.error(f"Error occurred in sending fcm notification for trip complate {trip.id}: {e}'")

    try:
        title=f"Hello {trip.driver.first_name}  {trip.driver.last_name}, Your ride completed"
        body=f"Hello {trip.driver.first_name}  {trip.driver.last_name}, Your have to reached your destination `{trip.destination}` and your ride has been complated"
        response_data=send_fcm_notification(driver.fcm_token, title, body)
        print(f'FCM notification {trip.id}: {response_data}')
        logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        print(f'Error sending fcm notification for trip cancel {trip.id}: {e}')
        logger.error(f"Error occurred in sending fcm notification for trip complate {trip.id}: {e}'")




def fcm_push_notification_arrived_at_pickup(trip_id, customer_id, driver_id):
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    # Notify customer and driver
    try:
        title=f"Driver {driver.first_name}  {driver.last_name} arrived your pick up location, pls go to the driver within 5 minutes, after 5 minutes waiting charges will be applied"
        body=f"Hello {customer.first_name}  {customer.last_name}, Your ride driver {driver.first_name} {driver.last_name} have reached near you, please contact with your rider throught of the number are {driver.phone}"
        response_data=send_fcm_notification(customer.fcm_token, title, body)
        logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending fcm notification for arrived at pickup locations {trip.id}: {e}'")









def send_fcm_notification_schedule(trip_id):
    scheduler = BackgroundScheduler()
    trip = Trip.objects.get(id=trip_id) 
    if trip.scheduled_datetime and timezone.now() <=  trip.scheduled_datetime - timedelta(hours=1):
        schedule_time=trip.scheduled_datetime - timedelta(hours=1)
        scheduled_time_str = trip.scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')
        title=f'Your trip is scheduled to start at {scheduled_time_str}.'
        body=f"Your trip is scheduled to start at {scheduled_time_str}, from {trip.source} to {trip.destination} "
        if trip.customer:
            token=trip.customer.fcm_token
            scheduler.add_job(
                send_fcm_notification,
                'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                run_date=schedule_time,  # Time to send the notification
                args=[token, title, body]  # Arguments for the functio
                )
            # Start the scheduler
            scheduler.start()
        if trip.driver:
            driver_fcm_token=trip.driver.fcm_token
            scheduler.add_job(
                send_fcm_notification,
                'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                run_date=schedule_time,  # Time to send the notification
                args=[driver_fcm_token, title, body]  # Arguments for the functio
                )
            # Start the scheduler
            scheduler.start()
           






