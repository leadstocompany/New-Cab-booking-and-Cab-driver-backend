from trips.models import Trip
from django.db.models import Q
from accounts.models import User, CurrentLocation
from subscriptions.models import Subscriptions
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from decimal import Decimal
from datetime import datetime, timedelta
import requests
import logging
logger = logging.getLogger(__name__)
def get_nearest_driver_list(trip_id, latitude, longitude):
    try:
        trip = Trip.objects.get(id=trip_id)
        max_distance = 15.0  # This could be made dynamic
        radius = 6371  # Earth's radius in kilometers

        def haversine(lat1, lon1, lat2, lon2):
            import math
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return radius * c

        active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
        drivers_without_active_trips = User.objects.filter(
            type=User.Types.DRIVER, driver_duty=True
        ).exclude(
            Q(driver_trips__status__in=active_trip_statuses)
        ).distinct()
        if trip.ride_type_id:
          
            drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=trip.ride_type_id)

        nearby_drivers = []

        for driver in drivers_without_active_trips:
            try:
                if driver.profile_status not in ["Block", "Rejected"]:
                    subscription = Subscriptions.objects.filter(driver=driver, is_active=True, payment_status="PAID").first()
                    # if subscription and subscription.pending_rides > 0:
                    if subscription:
                        
                        if not subscription.is_expired():
                            location = driver.currentlocation
                            distance = haversine(float(latitude), float(longitude), float(location.current_latitude), float(location.current_longitude))
                            if distance <= max_distance:
                                # Check if the driver has any unpaid completed trips
                                has_unpaid_trips = Trip.objects.filter(
                                    driver=driver,
                                    status='COMPLETED',
                                    payment_status__isnull=True  # Unpaid trips have empty payment_status
                                ).exists()
                                if not has_unpaid_trips:
                                    nearby_drivers.append(driver)              
            except CurrentLocation.DoesNotExist as e:
                logger.error(f"Error occurred: {e}")
                continue
        logger.debug("Processing data: nearst drivers list")
        return nearby_drivers
    except Exception as e:
        logger.error(f"Error occurred: {e}")


def get_all_available_drivers(return_object=False):
    """Get list of all available drivers"""
    try:
        # Get drivers who are on duty and not on active trips
        active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
        available_drivers = User.objects.filter(
            type=User.Types.DRIVER, 
            driver_duty=True,
            profile_status="Approve",
        ).exclude(
            Q(driver_trips__status__in=active_trip_statuses)
        ).distinct()

        logger.debug("Retrieved all available drivers list")
        if return_object:
            return available_drivers
        # return available_drivers
        drivers_ = []
        for driver in available_drivers:
            try:
                current_location = CurrentLocation.objects.get(user=driver)
                drivers_.append(
                    {
                        "lat": float(current_location.current_latitude),
                        "lng": float(current_location.current_longitude),

                    }
                )
            except CurrentLocation.DoesNotExist as e:
                logger.error(f"Error occurred: {e}")
                continue  
        return drivers_
    except Exception as e:
        logger.error(f"Error getting available drivers: {e}")


