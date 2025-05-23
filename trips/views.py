from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from couponcode.models import Coupon, CouponUsage
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

    def create(self, request, *args, **kwargs):
        try:
            trip = Trip.objects.get(id=request.data.get('trip_id'))
            
            # Get IDs from request or fallback to defaults
            driver_id = trip.driver.id
            customer_id = request.user.id

            data = {
                'trip': trip.id,
                'driver': driver_id,
                'customer': customer_id,
                'star': request.data.get('star'),
                'feedback': request.data.get('feedback', ''),
                'feedbacksetting': request.data.get('feedbacksetting', '')
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Trip.DoesNotExist:
            return Response(
                {"error": "Trip not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
        coupon_code = request.data.get('coupon_code', None)

        
        if payment_type.lower() == 'wallet':
            wallet_data = Wallet.objects.get(user=customer)
            if not trip_rent_price  and not ride_type_id:
                all_ride_type_prices = CabBookingPrice.objects.all()
                for ride_type_ in all_ride_type_prices: 
                    trip_base_fare_ = float(ride_type_.base_fare) * distance
                    if wallet_data.balance < trip_base_fare_:
                        return Response({"detail": "Insufficient balance. Atleast "+str(trip_base_fare_)+" required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
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
            distance=distance,
            coupon_code=coupon_code if coupon_code is not None or coupon_code !="" else None
        )
        print("trip")
        print(trip.created_at)
        logger.error("trip")
        logger.error(trip.created_at)


        # Notify drivers asynchronously
        if scheduled_datetime:
            # Notify driver 15 minutes before scheduled time
            indonesian_timezone = pytz.timezone(settings.TIME_ZONE)

            if isinstance(scheduled_datetime, str):  # Ensure it's not already a datetime object
                scheduled_datetime = parse_datetime(scheduled_datetime)

            # Step 2: Localize only if it's naive (without timezone)
            if scheduled_datetime.tzinfo is None:
                scheduled_datetime = indonesian_timezone.localize(scheduled_datetime)

            # Step 3: Convert to UTC
            scheduled_datetime = scheduled_datetime.astimezone(pytz.utc)
            notification_time = scheduled_datetime - timedelta(minutes=15)
            print(notification_time)
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
        if trip.rent_price is None or trip.rent_price <= 0:
            cab_price = CabBookingPrice.objects.get(cab_class_id=ride_type_id)
            trip.rent_price = cab_price.base_fare * trip.distance
        if trip.coupon_code:
            coupon = Coupon.objects.get(code=trip.coupon_code)
            CouponUsage.objects.create(user=trip.customer, coupon=coupon)
            coupon.use_count -= 1
            discount_price = (trip.rent_price * coupon.discount) / 100
            trip.rent_price = trip.rent_price - discount_price
            coupon.save()
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
            if trip.status == 'REQUESTED' and user.type == User.Types.CUSTOMER:
                trip.delete()
                return Response({"detail": "Trip cancelled successfully."}, status=status.HTTP_200_OK)
            elif trip.status not in ['CANCELLED', 'COMPLETED', 'ON_TRIP']:
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
                # trip.status = 'COMPLETED'
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
            

        schedule_ride = Trip.objects.filter(
            customer=self.request.user,
            scheduled_datetime__isnull=False,
            scheduled_datetime__lte=timezone.localtime()
        ).exclude(status__in=['ACCEPTED', 'REJECTED', 'CANCELLED', 'ON_TRIP', '']).order_by('-created_at')
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
        cancelled_ride=Trip.objects.filter(status__in=['CANCELLED', 'REJECTED'],customer=self.request.user).order_by('-created_at')
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


class PickupRadiusView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PickupRadius.objects.all()
    serializer_class = PickupRadiusSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            # Ensure only one record exists
            pickup_radius = PickupRadius.objects.first()
            if not pickup_radius:
                return Response({"detail": "No data found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(pickup_radius)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        pickup_radius = PickupRadius.objects.first()
        if not pickup_radius:
            return Response({"detail": "No data found to update."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(pickup_radius, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pickup_radius = PickupRadius.objects.first()
        if not pickup_radius:
            return Response({"detail": "No data found to delete."}, status=status.HTTP_404_NOT_FOUND)
        pickup_radius.delete()
        return Response({"detail": "Pickup radius deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PickupRadiusCreateView(generics.CreateAPIView):
    queryset = PickupRadius.objects.all()
    serializer_class = PickupRadiusSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        if PickupRadius.objects.exists():
            return Response({"detail": "Only one record is allowed."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)