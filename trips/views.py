from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from trips.models import *
from trips import serializers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from admin_api.serializers import FeedbackSettingSerializer
from admin_api.models import FeedbackSetting
from .tasks import notify_drivers, notify_trip_accepted
# Create your views here.

class DriverTripAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TripSerializer
    def get_queryset(self):
        return Trip.objects.filter(is_active=True, driver=self.request.user)
    
    # def perform_create(self, serializer):  
    #     serializer.save()
        # if serializer.instance.driver:
        #     channel_layer = get_channel_layer()
        #     async_to_sync(channel_layer.group_send)(
        #     "trip-notify_"+str(serializer.instance.cab.cab_class.id),
        #     {
        #         'type': 'trip_notify_message',
        #         'trip_data': serializer.data
        #     }
        # )

class DriverTripUpdateAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TripSerializer
    def get_queryset(self):
        return Trip.objects.filter(pk=self.kwargs.get("pk"), is_active=True)
    
    # def perform_update(self, serializer):
    #     serializer.save()
    #     if serializer.instance.driver \
    #         and serializer.instance.status == "REJECTED" or serializer.instance.status is None:
    #         channel_layer = get_channel_layer()
    #         async_to_sync(channel_layer.group_send)(
    #         "trip-notify_"+str(serializer.instance.cab.cab_class.id),
    #         {
    #             'type': 'trip_notify_message',
    #             'trip_data': serializer.data
    #         }
    #     )


class TripRatingAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.TripRatingSerializer
    def get_queryset(self):
        return TripRating.objects.filter(is_active=True, trip__customer=self.request.user)


class DriverPricingRatioAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DriverPricingRatioSerializer
    def get_queryset(self):
        return DriverPricingRatio.objects.all()
    

class ActiveFeedbackSettingList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FeedbackSettingSerializer


    def get_queryset(self):
        return FeedbackSetting.objects.filter(active=True)




# class BookingRequestView(APIView):
#     def post(self, request, *args, **kwargs):
#         customer = request.user
#         source = request.data.get('source')
#         destination = request.data.get('destination')
#         ride_type_id = request.data.get('ride_type')
#         latitude = float(request.data.get('latitude'))
#         longitude = float(request.data.get('longitude'))
#         trip_rent_price=request.data.get('trip_rent_price')
#         # Find nearest drivers without active trips
#         max_distance = 5.0  # This could be made dynamic
#         radius = 6371  # Earth's radius in kilometers

#         def haversine(lat1, lon1, lat2, lon2):
#             lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#             dlat = lat2 - lat1
#             dlon = lon2 - lon1
#             a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
#             c = 2 * math.asin(math.sqrt(a))
#             return radius * c

#         active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
#         drivers_without_active_trips = User.objects.filter(
#             type=User.Types.DRIVER, driver_duty=True
#         ).exclude(
#             Q(driver_trips__status__in=active_trip_statuses)
#         ).distinct()

#         if ride_type_id:
#             drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=ride_type_id)

#         nearby_drivers = []

#         for driver in drivers_without_active_trips:
#             try:
#                 location = driver.currentlocation
#                 distance = haversine(latitude, longitude, location.current_latitude, location.current_longitude)
#                 if distance <= max_distance:
#                     nearby_drivers.append(driver)
#             except CurrentLocation.DoesNotExist:
#                 continue

#         # Create trip request
#         trip = Trip.objects.create(
#             customer=customer,
#             source=source,
#             destination=destination,
#             ride_type_id=ride_type_id,
#             trip_rent_price=trip_rent_price,
#             status='REQUESTED'

#         )

#         # Notify drivers (pseudo code, replace with actual notification logic)
#         for driver in nearby_drivers:
#             notify_driver(driver, trip)

#         return Response({"detail": "Booking request sent to nearest drivers."}, status=status.HTTP_200_OK)

# def notify_driver(driver, trip):
#     # Implement notification logic here, e.g., sending a push notification
#     pass

# class AcceptTripView(APIView):
#     def post(self, request, trip_id, *args, **kwargs):
#         driver = request.user

#         try:
#             trip = Trip.objects.get(id=trip_id)
#             if trip.status != 'REQUESTED':
#                 return Response({"detail": "This trip is no longer available."}, status=status.HTTP_400_BAD_REQUEST)

#             trip.driver = driver
#             trip.status = 'BOOKED'
#             trip.save()

#             # Notify other drivers that the trip is no longer available
#             notify_other_drivers(trip)

#             return Response({"detail": "Trip accepted successfully."}, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             return Response({"detail": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)



class BookingRequestView(APIView):
    def post(self, request, *args, **kwargs):
        customer = request.user
        source = request.data.get('source')
        destination = request.data.get('destination')
        ride_type_id = request.data.get('ride_type')
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        trip_rent_price = request.data.get('trip_rent_price')

        # Create trip request
        trip = Trip.objects.create(
            customer=customer,
            source=source,
            destination=destination,
            ride_type_id=ride_type_id,
            trip_rent_price=trip_rent_price,
            status='REQUESTED',
            # latitude=latitude,
            # longitude=longitude
        )

        # Notify drivers asynchronously
        notify_drivers.delay(trip.id)

        return Response({"detail": "Booking request sent to nearest drivers."}, status=status.HTTP_200_OK)

class AcceptTripView(APIView):
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        driver_id = request.user.id

        notify_trip_accepted.delay(trip_id, driver_id)

        return Response({"detail": "Trip accepted successfully."}, status=status.HTTP_200_OK)