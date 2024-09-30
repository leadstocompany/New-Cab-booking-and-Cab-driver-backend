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

def get_nearest_driver_list(trip_id, latitude, longitude):
    try:
        trip = Trip.objects.get(id=trip_id)
        max_distance = 5.0  # This could be made dynamic
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
                subscription = Subscriptions.objects.filter(driver=driver, is_active=True, payment_status="PAID").first()
                # if subscription and subscription.pending_rides > 0:
                if subscription:
                    
                    if not subscription.is_expired():
                        location = driver.currentlocation
                        distance = haversine(float(latitude), float(longitude), float(location.current_latitude), float(location.current_longitude))
                        if distance <= max_distance:
                            nearby_drivers.append(driver)
                    
            except CurrentLocation.DoesNotExist:
                continue
        # # Notify drivers
        # for driver in nearby_drivers:
        #     print("yes")
        #     booking_request_notify_driver(driver, trip, scheduled_datetime)
        return nearby_drivers
    except Exception as e:
        print("celery error :", e)
