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
from utility.util import get_notification_mapping, render_notification_template
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logger = logging.getLogger(__name__)

def fcm_push_notification_trip_booking_request_to_drivers(trip_id, drivers, scheduled_datetime):
    try:
        trip = Trip.objects.get(id=trip_id)

        for driver in drivers:
            try:
                mapping = get_notification_mapping(trip_id=trip_id, driver=driver, extra_mapping={"PaymentAmount": trip.rent_price})
                title, body = render_notification_template('TripBookingRequest', mapping)
                if title and body:
                    response_data = send_fcm_notification(driver.fcm_token, title, body)
                    logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
            except Exception as e:
                logger.error(f"Error occurred in sending FCM notification for trip request {trip.id}: {e}")
    except Exception as e:
        logger.error(f"Trip request {trip.id}: {e}")


def fcm_push_notification_trip_accepted(trip_id):
    trip = Trip.objects.get(id=trip_id)
    try:
        mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})
        title, body = render_notification_template('TripAccepted', mapping)
        if title and body:
            response_data = send_fcm_notification(trip.customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip accepted {trip.id}: {e}")


def fcm_push_notification_trip_cancelled(trip_id, user_type, cancel_reason):
    trip = Trip.objects.get(id=trip_id)
    mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})
    mapping['CancelReason'] = cancel_reason

    if user_type == 'driver':
        try:
            title, body = render_notification_template('TripCancelled', mapping)
            if title and body:
                response_data = send_fcm_notification(trip.driver.fcm_token, title, body)
                logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
        except Exception as e:
            logger.error(f"Error occurred in sending FCM notification for trip cancel {trip.id}: {e}")
    elif user_type == 'customer':
        try:
            title, body = render_notification_template('TripCancelled', mapping)
            if title and body:
                response_data = send_fcm_notification(trip.customer.fcm_token, title, body)
                logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
        except Exception as e:
            logger.error(f"Error occurred in sending FCM notification for trip cancel {trip.id}: {e}")


def fcm_push_notification_trip_started(trip_id):
    trip = Trip.objects.get(id=trip_id)
    try:
        mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})
        title, body = render_notification_template('TripStart', mapping)
        if title and body:
            response_data = send_fcm_notification(trip.customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip start {trip.id}: {e}")


def fcm_push_notification_trip_completed(trip_id, customer_id, driver_id):
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})

    try:
        title, body = render_notification_template('TripComplete', mapping)
        if title and body:
            response_data = send_fcm_notification(customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip complete {trip.id}: {e}")

    try:
        title, body = render_notification_template('TripComplete', mapping)
        if title and body:
            response_data = send_fcm_notification(driver.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for trip complete {trip.id}: {e}")


def fcm_push_notification_arrived_at_pickup(trip_id, customer_id, driver_id):
    customer = User.objects.get(id=customer_id)
    driver = User.objects.get(id=driver_id)
    trip = Trip.objects.get(id=trip_id)
    mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})

    try:
        title, body = render_notification_template('TripDriverArrived', mapping)
        if title and body:
            response_data = send_fcm_notification(customer.fcm_token, title, body)
            logger.info(f"FCM notification Processing data {trip.id}: {response_data}")
    except Exception as e:
        logger.error(f"Error occurred in sending FCM notification for arrived at pickup {trip.id}: {e}")


def send_fcm_notification_schedule(trip_id):
    scheduler = BackgroundScheduler()
    trip = Trip.objects.get(id=trip_id)

    if trip.scheduled_datetime and timezone.now() <= trip.scheduled_datetime - timedelta(hours=1):
        schedule_time = trip.scheduled_datetime - timedelta(hours=1)
        mapping = get_notification_mapping(trip_id=trip_id, extra_mapping={"PaymentAmount": trip.rent_price})

        # Render title and body using the active notification template
        title, body = render_notification_template('TripScheduled', mapping)

        if title and body:
            # Schedule notification for the customer
            if trip.customer:
                token = trip.customer.fcm_token
                scheduler.add_job(
                    send_fcm_notification,
                    'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                    run_date=schedule_time,  # Time to send the notification
                    args=[token, title, body]  # Arguments for the function
                )

            # Schedule notification for the driver
            if trip.driver:
                driver_fcm_token = trip.driver.fcm_token
                scheduler.add_job(
                    send_fcm_notification,
                    'date',  # Type of trigger (you can also use 'interval' for repeated notifications)
                    run_date=schedule_time,  # Time to send the notification
                    args=[driver_fcm_token, title, body]  # Arguments for the function
                )

            # Start the scheduler
            scheduler.start()







