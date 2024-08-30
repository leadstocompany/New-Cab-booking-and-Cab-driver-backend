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
from trips.tasks import booking_request_notify_drivers, notify_trip_accepted, notify_trip_cancelled, notify_trip_started,  notify_trip_completed, send_trip_schedule_notification
import random
from utility.pagination import CustomPagination
from JLP_MyRide import settings
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
import stripe
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
        ride_type_id = request.data.get('ride_type')
        trip_rent_price = request.data.get('trip_rent_price')
        scheduled_datetime=request.data.get('scheduled_datetime', None)
        payment_type= request.data.get('payment_type')
        otp = str(random.randint(1000, 9999))
        
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
        )

        # Notify drivers asynchronously
        booking_request_notify_drivers.delay(trip.id, pickup_latitude, pickup_longitude, scheduled_datetime)
        # response_data =notify_drivers(trip.id, pickup_latitude, pickup_longitude, scheduled_datetime)
        return Response({"detail": "Booking request sent to nearest drivers.", "otp":otp, 'trip_id':trip.id}, status=status.HTTP_200_OK)

class AcceptTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        driver= request.user
        cab=Vehicle.objects.filter(driver=driver).first()
        trip = Trip.objects.get(id=trip_id)
        if trip.status != 'REQUESTED':
            return Response({"massege":"The trip already Booked"}, status=status.HTTP_400_BAD_REQUEST)

        trip.driver = driver
        trip.cab=cab
        trip.status = 'BOOKED'
        trip.save()

        notify_trip_accepted.delay(trip_id)
        # respoinse=notify_trip_accepted(trip_id)
        if trip.scheduled_datetime:
            scheduled_datetime = datetime.strptime(trip.scheduled_datetime, '%Y-%m-%d %H:%M:%S')
            send_trip_schedule_notification.apply_async(
                (trip.id,),
                eta=scheduled_datetime - timedelta(hours=1)
            )

        return Response({"detail": "Trip accepted successfully."}, status=status.HTTP_200_OK)


class CancelTripView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        user = request.user
        cancel_reason = request.data.get('cancel_reason')

        try:
            trip = Trip.objects.get(id=trip_id)
            if trip.status not in ['CANCELLED', 'COMPLETED', 'ON_TRIP']:
                trip.status = 'CANCELLED'
                trip.canceled_by = user
                trip.cancel_reason = cancel_reason
                trip.save()
                if user.type == User.Types.DRIVER:
                    notify_trip_cancelled.delay(trip.id, trip.customer.id, 'customer', cancel_reason)
                else:
                    notify_trip_cancelled.delay(trip.id, trip.driver.id, 'driver', cancel_reason)
                return Response({"detail": "Trip cancelled successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Trip cannot be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
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
                    trip.save()
                    notify_trip_started.delay(trip_id)
                    # notify_trip_started(trip_id)
                    return Response({"detail": "Trip started successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
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
                trip.save()
                notify_trip_completed.delay(trip.id, trip.customer.id, trip.driver.id)
                # notify_trip_completed(trip.id, trip.customer.id, trip.driver.id)
                return Response({"detail": "Trip completed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Trip cannot be completed or you are not the assigned driver."}, status=status.HTTP_400_BAD_REQUEST)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip does not exist."}, status=status.HTTP_404_NOT_FOUND)


class CompletedRidesListView(generics.ListAPIView):
    serializer_class = TripSerializer
    # pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get the current authenticated user
        user = self.request.user
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        total_rent_price = Trip.objects.filter(status='COMPLETED', driver=user).aggregate(Sum('rent_price'))['rent_price__sum'] or 0
        # If total_rent_price is None, default to 0
        total_rent_price = total_rent_price or 0
        # Filter trips where the status is 'ON_TRIP' and the driver is the authenticated user
        response_data = {
            "total_trips":Trip.objects.filter(status='COMPLETED', driver=user).count(),
            "tatal_distance":total_distance,
            "total_earing":total_rent_price,
            "ride_history":Trip.objects.filter(status='COMPLETED', driver=user)

        }
        return response_data

class ScheduledRideListView(generics.ListAPIView):
    serializer_class = TripSerializer
    # pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get all trips where scheduled_datetime is in the future
        user = self.request.user
        now = timezone.now()
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        today = timezone.now().date()

        # Filter trips by status, driver, and today's date
        today_total_rent_price = Trip.objects.filter(
            status='COMPLETED',
            driver=user,
            created_at__date=today  # Assuming the `scheduled_datetime` is the date field to compare
        ).aggregate(Sum('rent_price'))['rent_price__sum'] or 0
        response_data={
            "total_schedule_trips":Trip.objects.filter(scheduled_datetime__isnull=False, scheduled_datetime__gt=now, driver=user).count(),
            "total_distance":total_distance,
            "today's_earging": today_total_rent_price,
            "schedule_trips":Trip.objects.filter(scheduled_datetime__isnull=False, scheduled_datetime__gt=now, driver=user)
        }
        return response_data

class CurrentRidesListView(generics.ListAPIView):
    serializer_class = TripSerializer
    # pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get the current authenticated user
        user = self.request.user
        total_distance = Trip.objects.filter(status='COMPLETED', driver=user, distance__isnull=False ).aggregate(Sum('distance'))['distance__sum'] or 0
        # If total_distance is None, default to 0
        total_distance = total_distance or 0
        today = timezone.now().date()

        # Filter trips by status, driver, and today's date
        today_total_rent_price = Trip.objects.filter(
            status='COMPLETED',
            driver=user,
            created_at__date=today  # Assuming the `scheduled_datetime` is the date field to compare
        ).aggregate(Sum('rent_price'))['rent_price__sum'] or 0
        # Filter trips where the status is 'ON_TRIP' and the driver is the authenticated user
        current_trip_statuses = ['REQUESTED', 'ACCEPTED', 'BOOKED', 'ON_TRIP']
        response_data = {
            "current_trips":Trip.objects.filter(status__in=current_trip_statuses,driver=user).count(),
            "tatal_distance":total_distance,
            "today's_earing":today_total_rent_price,
            "current_ride":Trip.objects.filter(status__in=current_trip_statuses,driver=user)

        }
        return response_data
# payment type = case, UPI, WALLET, QRcode


class PassengerTripListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        

        # Filter trips based on status
        
        complete_ride=Trip.objects.filter(status='COMPLETED',customer=self.request.user)
        # Serialize the filtered trips
        complete_ride_serializer = TripSerializer(complete_ride, many=True)
        schedule_ride=Trip.objects.filter(status='BOOKED',customer=self.request.user, scheduled_datetime__isnull=False)
        # Serialize the filtered trips
        schedule_ride_serializer = TripSerializer(schedule_ride, many=True)
        active_ride=Trip.objects.filter(status='ON_TRIP',customer=self.request.user)
        active_ride_serializer = TripSerializer(active_ride, many=True)
        cancelled_ride=Trip.objects.filter(status='CANCELLED',customer=self.request.user)
        cancelled_ride_serializer = TripSerializer(cancelled_ride, many=True)
        response_data={
            "active_ride":active_ride_serializer.data,
            "schedule_ride":schedule_ride_serializer.data,
            "complete_rid":complete_ride_serializer.data,
            "cancelled_ride":cancelled_ride_serializer.data,
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