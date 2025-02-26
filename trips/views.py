from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from trips.models import *
from trips.serializers import *
from admin_api.serializers import FeedbackSettingSerializer, DriverFeedbackPageSerializer
from admin_api.models import FeedbackSetting, DriverFeedbackPage
from trips.tasks import booking_request_notify_drivers, notify_trip_accepted, notify_trip_cancelled, notify_trip_started,  notify_trip_completed, schedule_driver_notifications, send_trip_schedule_notification, notify_arrived_at_pickup,notify_trip_request_cancel
from trips.fcm_notified_task import fcm_push_notification_trip_booking_request_to_drivers, fcm_push_notification_trip_accepted, fcm_push_notification_trip_cancelled, fcm_push_notification_trip_started, fcm_push_notification_trip_completed, fcm_push_notification_arrived_at_pickup, send_fcm_notification_schedule
from utility.nearest_driver_list import get_nearest_driver_list
import random
from utility.pagination import CustomPagination
from JLP_MyRide import settings
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
import stripe
import json
from utility.rating import get_driver_rating
import logging
import pytz

from utility.util import parse_datetime
from wallets.models import Wallet
logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

class TripRatingAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TripRatingSerializer
    def get_queryset(self):
        return TripRating.objects.filter(is_active=True, trip__customer=self.request.user)




class ActiveFeedbackSettingList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FeedbackSettingSerializer


    def get_queryset(self):
        return FeedbackSetting.objects.filter(active=True)
    
class DriverActiveFeedbackPageList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DriverFeedbackPageSerializer
    def get_queryset(self):
        return DriverFeedbackPage.objects.filter(active=True)





class BookingRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        customer = request.user
        source = request.data.get('source')
        destination = request.data.get('destination')
        pickup_latitude=request.data.get('pickup_latitude')
        pickup_longitude=request.data.get('pickup_longitude')
        dropup_latitude=request.data.get('dropup_latitude')
        dropup_longitude= request.data.get('dropup_longitude')
        ride_type_id = request.data.get('ride_type', None)
        trip_rent_price = request.data.get('trip_rent_price')
        scheduled_datetime=request.data.get('scheduled_datetime', None)
        payment_type= request.data.get('payment_type')
        distance=request.data.get('distance')
        otp = str(random.randint(1000, 9999))

        
        if payment_type.lower() == 'wallet':
            wallet_data = Wallet.objects.get(user=customer)
            if wallet_data.balance < trip_rent_price:
                return Response({"detail": "Insufficient balance. Atleast "+str(trip_rent_price)+" required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create trip request
        trip = Trip.objects.create(
            customer=customer,
            source=source,
            destination=destination,
            ride_type_id=ride_type_id,
            rent_price=trip_rent_price,
            status='REQUESTED',
            otp=otp,
            pickup_latitude=pickup_latitude,
            pickup_longitude=pickup_longitude,
            dropup_latitude=dropup_latitude,
            dropup_longitude= dropup_longitude,
            scheduled_datetime=scheduled_datetime,
            payment_type=payment_type,
            distance=distance
        )

        # Notify drivers asynchronously
        if scheduled_datetime:
            # Notify driver 15 minutes before scheduled time
            scheduled_datetime = parse_datetime(scheduled_datetime)
            scheduled_datetime = pytz.utc.localize(scheduled_datetime)
            notification_time = scheduled_datetime - timedelta(minutes=15)
            schedule_driver_notifications.apply_async(
                args=[trip.id, pickup_latitude, pickup_longitude, scheduled_datetime],
                eta=notification_time
            )
        else:
            schedule_driver_notifications.delay(trip.id, pickup_latitude, pickup_longitude, None)
       
        return Response({"detail": "Booking request sent to nearest drivers.", "otp":otp, 'trip_id':trip.id}, status=status.HTTP_200_OK)

class AcceptTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        ride_type_id = request.data.get('ride_type_id', None)
        
        driver= request.user
        cab=Vehicle.objects.filter(driver=driver).first()
        trip = Trip.objects.get(id=trip_id)
        if trip.status != 'REQUESTED':
            return Response({"massege":"The trip already Booked"}, status=status.HTTP_400_BAD_REQUEST)

        trip.driver = driver
        trip.cab=cab
        if ride_type_id:
            trip.ride_type_id = ride_type_id
        if trip.rent_price is None:
            cab_price = CabBookingPrice.objects.get(cab_class_id=ride_type_id)
            trip.rent_price = cab_price.base_fare * trip.distance
        trip.status = 'BOOKED'
        trip.save()
        fcm_push_notification_trip_accepted(trip_id)
        notify_trip_accepted.delay(trip_id)
        # respoinse=notify_trip_accepted(trip_id)
        if trip.scheduled_datetime:
            send_fcm_notification_schedule(trip_id)
            
            # scheduled_datetime = datetime.strptime(trip.scheduled_datetime, '%Y-%m-%d %H:%M:%S')
            send_trip_schedule_notification.apply_async(
                (trip.id,),
                eta=trip.scheduled_datetime - timedelta(hours=1)
            )

        return Response({"detail": "Trip accepted successfully."}, status=status.HTTP_200_OK)


class CancelTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        user = request.user
        cancel_reason = request.data.get('cancel_reason')
        ride_type_id = request.data.get('ride_type_id', None)

        try:
            trip = Trip.objects.get(id=trip_id)
            if trip.status not in ['CANCELLED', 'COMPLETED', 'ON_TRIP']:
                trip.status = 'CANCELLED'
                trip.canceled_by = user
                trip.cancel_reason = cancel_reason
                if ride_type_id:
                    trip.ride_type_id = ride_type_id
                trip.save()
                if user.type == User.Types.DRIVER:
                    fcm_push_notification_trip_cancelled(trip_id,'customer', cancel_reason)
                    notify_trip_cancelled.delay(trip.id, trip.customer.id, 'customer', cancel_reason)
                    
                else:
                    if trip.driver:
                        fcm_push_notification_trip_cancelled(trip_id,'driver', cancel_reason)
                        notify_trip_cancelled.delay(trip.id, trip.driver.id, 'driver', cancel_reason)
                    else:
                        drivers=get_nearest_driver_list(trip.id, trip.pickup_latitude, trip.pickup_longitude)
                        driver_ids = [driver.id for driver in drivers]
                        notify_trip_request_cancel.delay(trip.id, driver_ids, cancel_reason)

                return Response({"detail": "Trip cancelled successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Trip cannot be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            logger.error(f"Trip does not exist")
            return Response({"detail": "Trip does not exist."}, status=status.HTTP_404_NOT_FOUND)
        



class VerifyOTPAndStartTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        otp = request.data.get('otp')
        driver = request.user

        try:
            trip = Trip.objects.get(id=trip_id)
            if trip.status == "BOOKED" and trip.driver==driver:
                if trip.otp == otp:
                    trip.status = 'ON_TRIP'
                    trip.ride_start_time=timezone.localtime(timezone.now())
                    trip.save()
                    fcm_push_notification_trip_started(trip_id)
                    notify_trip_started.delay(trip_id)
                    # notify_trip_started(trip_id)
                    return Response({"detail": "Trip started successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            logger.error(f"Trip does not exist")
            return Response({"detail": "Trip does not exist or you are not authorized to start this trip."}, status=status.HTTP_404_NOT_FOUND)



class CompleteTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        user = request.user

        try:
            trip = Trip.objects.get(id=trip_id)
            if trip.status == 'ON_TRIP' and trip.driver == user:
                trip.status = 'COMPLETED'
                trip.ride_end_time=timezone.localtime(timezone.now())
                trip.save()
                fcm_push_notification_trip_completed(trip.id, trip.customer.id, trip.driver.id)
                notify_trip_completed.delay(trip.id, trip.customer.id, trip.driver.id)
                # notify_trip_completed(trip.id, trip.customer.id, trip.driver.id)
                return Response({"detail": "Trip completed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Trip cannot be completed or you are not the assigned driver."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            logger.error(f"Trip does not exist")
            return Response({"detail": "Trip does not exist."}, status=status.HTTP_404_NOT_FOUND)


class ArrivedAtPickupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        user = request.user
        try:
            trip = Trip.objects.get(id=trip_id)
            if trip.status == 'BOOKED' and trip.driver == user:
                trip.driver_arrived_at_pickup_time=timezone.localtime(timezone.now())
                trip.save()
                fcm_push_notification_arrived_at_pickup(trip.id, trip.customer.id, trip.driver.id)
                notify_arrived_at_pickup.delay(trip.id, trip.customer.id, trip.driver.id)
                # notify_arrived_at_pickup(trip.id, trip.customer.id, trip.driver.id)
                return Response({"detail": "Arrived at pickup successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "you are not the assigned driver."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            logger.error(f"Trip does not exist")
            return Response({"detail": "Trip does not exist."}, status=status.HTTP_404_NOT_FOUND)





class CompletedRidesListView(APIView):
 
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        # Get the current authenticated user
        user = self.request.user
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        total_rent_price = Trip.objects.filter(status='COMPLETED', driver=user,payment_status="paid").aggregate(Sum('total_fare'))['total_fare__sum'] or 0
        # If total_rent_price is None, default to 0
        total_rent_price = total_rent_price or 0
        # Filter trips where the status is 'ON_TRIP' and the driver is the authenticated user
        completed_trip=Trip.objects.filter(status='COMPLETED', driver=user).order_by('-created_at')
        response_data = {
            "total_trips":Trip.objects.filter(status='COMPLETED', driver=user).count(),
            "tatal_distance":total_distance,
            "total_earing":total_rent_price,
            "ride_history":TripSerializer(completed_trip, many=True).data
        }
        return Response(response_data, status=status.HTTP_200_OK)

        # return response_data
    

class ScheduledRideListView(APIView):
 
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        # Get all trips where scheduled_datetime is in the future
        user = self.request.user
        # now = timezone.now()
        now=timezone.localtime(timezone.now())
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        # today = timezone.now().date()
        today=timezone.localtime().date()

        # Filter trips by status, driver, and today's date
        today_total_rent_price = Trip.objects.filter(
            status='COMPLETED',
            driver=user,
            created_at__date=today  # Assuming the `scheduled_datetime` is the date field to compare
        ).aggregate(Sum('rent_price'))['rent_price__sum'] or 0
        schedule_trips=Trip.objects.filter(scheduled_datetime__isnull=False, scheduled_datetime__gt=now, driver=user, status="BOOKED").order_by('-created_at')
        schedule_trips_serializer = TripSerializer(schedule_trips, many=True)
        schedule_trips_data=schedule_trips_serializer.data
        for trip in schedule_trips_data:
            trip.pop('otp', None) 
        response_data={
            "total_schedule_trips":Trip.objects.filter(scheduled_datetime__isnull=False, scheduled_datetime__gt=now, driver=user).count(),
            "total_distance":total_distance,
            "today's_earging": today_total_rent_price,
            "schedule_trips":schedule_trips_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CurrentRidesListView(APIView):
 
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request): 
        # Get the current authenticated user
        user = self.request.user
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        # today = timezone.now().date()
        today=timezone.localtime().date()

        # Filter trips by status, driver, and today's date
        today_total_rent_price = Trip.objects.filter(
            status='COMPLETED',
            driver=user,
            created_at__date=today  # Assuming the `scheduled_datetime` is the date field to compare
        ).aggregate(Sum('rent_price'))['rent_price__sum'] or 0
        # Filter trips where the status is 'ON_TRIP' and the driver is the authenticated user
        current_trip_statuses = ['REQUESTED', 'ACCEPTED', 'BOOKED', 'ON_TRIP']
        current_ride=Trip.objects.filter(status__in=current_trip_statuses,driver=user).order_by('-created_at')
        current_ride_serializer = TripSerializer(current_ride, many=True)
        response_data = {
            "current_trips":Trip.objects.filter(status__in=current_trip_statuses,driver=user).count(),
            "tatal_distance":total_distance,
            "today's_earing":today_total_rent_price,
            "current_ride":current_ride_serializer.data

        }
        return Response(response_data, status=status.HTTP_200_OK)



class PassengerTripListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        # Filter trips based on status
        complete_ride=Trip.objects.filter(status='COMPLETED',customer=self.request.user).order_by("-created_at")
        # Serialize the filtered trips
        complete_ride_serializer = TripSerializer(complete_ride, many=True)
        # for com_ride in complete_ride_serializer.data:
        complete_ride_data = complete_ride_serializer.data
        for ride in complete_ride_data:
            try:
                driver_info = ride.get('driver')
                # print(driver_info)
                if driver_info:
                    driver=Driver.objects.get(id=driver_info['id'])
                    # Update the serialized data (this doesn't update the database directly)
                    driver_info['rating'] = get_driver_rating(driver)
                    driver_info['total_earing'] = Trip.objects.filter(status='COMPLETED', driver=driver,  payment_status="paid").aggregate(Sum('total_fare'))['total_fare__sum'] or 0
                    driver_info['total_distance'] =Trip.objects.filter(status='COMPLETED', driver=driver, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
                    driver_info['total_complete_trip'] = Trip.objects.filter(status='COMPLETED', driver=driver).count()
            except Exception as e:
                logger.error(f"Error occurred: {e}")
            

        schedule_ride=Trip.objects.filter(status='BOOKED',customer=self.request.user, scheduled_datetime__isnull=False).order_by('-created_at')
        # Serialize the filtered trips
        schedule_ride_serializer = TripSerializer(schedule_ride, many=True)
        schedule_ride_data=schedule_ride_serializer.data
        for ride in schedule_ride_data:
            try:
                driver_info = ride.get('driver')
                # print(driver_info)
                if driver_info:
                    driver=Driver.objects.get(id=driver_info['id'])
                    # Update the serialized data (this doesn't update the database directly)
                    driver_info['rating'] = get_driver_rating(driver)
                    driver_info['total_earing'] = Trip.objects.filter(status='COMPLETED', driver=driver,  payment_status="paid").aggregate(Sum('total_fare'))['total_fare__sum'] or 0
                    driver_info['total_distance'] =Trip.objects.filter(status='COMPLETED', driver=driver, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
                    driver_info['total_complete_trip'] = Trip.objects.filter(status='COMPLETED', driver=driver).count()
            except Exception as e:
                logger.error(f"Error occurred: {e}")
              
        active_ride=Trip.objects.filter(status__in=['ON_TRIP','BOOKED'] ,customer=self.request.user).order_by('-created_at')
        active_ride_serializer = TripSerializer(active_ride, many=True)
        active_ride_data = active_ride_serializer.data
        for ride in active_ride_data:
            try:
                driver_info = ride.get('driver')
                # print(driver_info)
                if driver_info:
                    driver=Driver.objects.get(id=driver_info['id'])
                    # Update the serialized data (this doesn't update the database directly)
                    driver_info['rating'] = get_driver_rating(driver)
                    driver_info['total_earing'] = Trip.objects.filter(status='COMPLETED', driver=driver,  payment_status="paid").aggregate(Sum('total_fare'))['total_fare__sum'] or 0
                    driver_info['total_distance'] =Trip.objects.filter(status='COMPLETED', driver=driver, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
                    driver_info['total_complete_trip'] = Trip.objects.filter(status='COMPLETED', driver=driver).count()
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                print(e)
        # cancelled_ride=Trip.objects.filter(status='CANCELLED',customer=self.request.user,driver__isnull=False)
        cancelled_ride=Trip.objects.filter(status='CANCELLED',customer=self.request.user).order_by('-created_at')
        cancelled_ride_serializer = TripSerializer(cancelled_ride, many=True)
        cancelled_ride_data=cancelled_ride_serializer.data
        for ride in cancelled_ride_data:
            try:
                driver_info = ride.get('driver')
                # print(driver_info)
                if driver_info:
                    driver=Driver.objects.get(id=driver_info['id'])
                    # Update the serialized data (this doesn't update the database directly)
                    driver_info['rating'] = get_driver_rating(driver)
                    driver_info['total_earing'] = Trip.objects.filter(status='COMPLETED', driver=driver,  payment_status="paid").aggregate(Sum('total_fare'))['total_fare__sum'] or 0
                    driver_info['total_distance'] =Trip.objects.filter(status='COMPLETED', driver=driver, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
                    driver_info['total_complete_trip'] = Trip.objects.filter(status='COMPLETED', driver=driver).count()
            except Exception as e:
                logger.error(f"Error occurred: {e}")
        

        response_data={
            "active_ride":active_ride_data,
            "schedule_ride":schedule_ride_data,
            "complete_ride":complete_ride_data,
            "cancelled_ride":cancelled_ride_data,
        }

        # Return the serialized data
        return Response(response_data, status=status.HTTP_200_OK)










# from trips.models import Trip
# from trips.notifications import booking_request_notify_driver, notify_trip_booked, send_real_time_notification
# from django.db.models import Q
# from accounts.models import User, CurrentLocation
# from subscriptions.models import Subscriptions
# from django.utils import timezone
# from datetime import timedelta
# from django.core.mail import send_mail
# from decimal import Decimal



# def notify_drivers(trip_id, latitude, longitude,scheduled_datetime):
   
#     trip = Trip.objects.get(id=trip_id)
#     max_distance = 5.0  # This could be made dynamic
#     radius = 6371  # Earth's radius in kilometers

#     def haversine(lat1, lon1, lat2, lon2):
#         import math
#         lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#         dlat = lat2 - lat1
#         dlon = lon2 - lon1
#         a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
#         c = 2 * math.asin(math.sqrt(a))
#         return radius * c

#     active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
#     drivers_without_active_trips = User.objects.filter(
#         type=User.Types.DRIVER, driver_duty=True
#     ).exclude(
#         Q(driver_trips__status__in=active_trip_statuses)
#     ).distinct()
#     print(trip.ride_type)
#     if trip.ride_type_id:
#         print("yes one")
#         drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=trip.ride_type_id)

#     nearby_drivers = []

#     for driver in drivers_without_active_trips:
#         # print("yes two")
#         try:
#             subscription = Subscriptions.objects.filter(driver=driver, is_active=True).first()
#             # if subscription and subscription.pending_rides > 0:
#             if subscription:
                 
#                 if not subscription.is_expired():
#                     location = driver.currentlocation
#                     print(location.current_latitude, location.current_longitude)
#                     print("yes two")
#                     #  location = driver.currentlocation
#                     distance = haversine(float(latitude), float(longitude), float(location.current_latitude), float(location.current_longitude))
#                     print(distance, "or", max_distance)
#                     if distance <= max_distance:
#                         nearby_drivers.append(driver)
                
#         except CurrentLocation.DoesNotExist:
#             continue
#     print(nearby_drivers, "10000000000000000000000000")
#     # Notify drivers
#     for driver in nearby_drivers:
#         print("yes")
#         booking_request_notify_driver(driver, trip, scheduled_datetime)



# def notify_trip_accepted(trip_id, driver):
#     trip = Trip.objects.get(id=trip_id)
#     # if trip.status != 'REQUESTED':
#     #     return

#     # trip.driver = driver
#     # trip.status = 'BOOKED'
#     # trip.save()

#     # Notify the customer
#     notify_trip_booked(trip.customer, trip)

#     # Notify other drivers that the trip has been booked
#     # other_drivers = trip.driver_trips.filter(status='REQUESTED').exclude(driver=driver)
#     # for other_driver in other_drivers:
#     #     notify_trip_booking_closed(other_driver, trip)