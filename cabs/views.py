from django.shortcuts import render
from rest_framework import generics, permissions, status
from cabs.models import *
from cabs.serializers import CabTypeSerializer, CabClassSerializer, VehicleMakerSerializer, VehicleModelSerializer, VehicleLocationUpdateSerializer, VehicaleDetailsSerializer, CabBookingPriceSerializer, NearestDriverSerializer
from geopy.distance import geodesic
from rest_framework.views import APIView
from rest_framework.response import Response
from trips.models import Trip
import math
from django.db.models import Q
from subscriptions.models import Subscriptions
from rest_framework.exceptions import NotFound
import logging
logger = logging.getLogger(__name__)
# Create your views here.

class CabTypeAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CabTypeSerializer
    queryset = CabType.objects.filter(is_active=True)

class CabClassAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CabClassSerializer
    def get_queryset(self):
        return CabClass.objects.filter(cab_type=self.kwargs.get("pk"), is_active=True)

class VehicleMakerAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicleMakerSerializer
    def get_queryset(self):
        return VehicleMaker.objects.filter(cab_type=self.kwargs.get("pk"), is_active=True)
        # return VehicleMaker.objects.filter(is_active=True)

# class VehicleModelAPI(generics.ListAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = VehicleModelSerializer
#     def get_queryset(self):
#         return VehicleModel.objects.filter(maker_id=self.kwargs.get("pk"), is_active=True)
class VehicleModelAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicleModelSerializer

    def get_queryset(self):
        # Retrieve URL parameters
        cab_type_id = self.kwargs.get('cab_type_id')
        cab_maker_id = self.kwargs.get('cab_maker_id')

        # Filter VehicleModel based on cab_maker_id and is_active status
        queryset = VehicleModel.objects.filter(maker_id=cab_maker_id, is_active=True)

        # Optionally, filter by cab_type_id if needed
        if cab_type_id:
            queryset = queryset.filter(cabtype_id=cab_type_id)
        
        return queryset

class VehicleLocationUpdateAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicleLocationUpdateSerializer
    def get_queryset(self):
        return Vehicle.objects.filter(pk=self.kwargs.get("pk"), is_active=True)

class VehicaleDetailsAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicaleDetailsSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(driver=self.request.user, is_active=True)

class GetVehicaleDetailsAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicaleDetailsSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(pk=self.kwargs.get("pk"), is_active=True)

class CabClassWithPriceList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        cab_booking_prices = CabBookingPrice.objects.all()
        serializer = CabBookingPriceSerializer(cab_booking_prices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class NearbyVehiclesAPIView(APIView):

#     def get(self, request, format=None):
#         user_lat = request.query_params.get('latitude')
#         user_lon = request.query_params.get('longitude')
#         cab_class = request.query_params.get('cab_class')
        
#         if not user_lat or not user_lon or not cab_class:
#             return Response({"error": "Missing latitude, longitude or cab class parameter"}, status=status.HTTP_400_BAD_REQUEST)

#         user_coordinates = (float(user_lat), float(user_lon))
#         nearby_vehicles = []
#         vehicles = Vehicle.objects.filter(driver__driver_duty=True, is_approved=True, cab_class__id=cab_class)

#         search_radii = [1, 2, 5]  # Radii to search in km
#         for radius in search_radii:
#             for vehicle in vehicles:
#                 try:
#                     vehicle_coordinates = (float(vehicle.last_latitude), float(vehicle.last_longitude))
#                     distance = geodesic(user_coordinates, vehicle_coordinates).km

#                     if distance <= radius:
#                          # Check if the vehicle is free
#                         active_trips = Trip.objects.filter(cab=vehicle, status__in=['ON_TRIP', 'BOOKED'])
#                         if not active_trips.exists():
#                             nearby_vehicles.append(vehicle)
                        
#                 except (ValueError, TypeError):
#                     continue

#             if nearby_vehicles:
#                 break  # Exit the loop if vehicles are found within the current radius

#         if not nearby_vehicles:
#             return Response({"message": "No vehicles found within 5 km."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = VehicaleDetailsSerializer(nearby_vehicles, many=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)




class NearestDriversView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request,cab_class_id, latitude, longitude, max_distance=15, *args, **kwargs):
        max_distance = float(max_distance)
        radius = 6371  # Earth's radius in kilometers

        def haversine(lat1, lon1, lat2, lon2):
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return radius * c

        # Get all drivers who are not on an active trip
        active_trip_statuses = ['ACCEPTED', 'BOOKED', 'ON_TRIP']
        drivers_without_active_trips = User.objects.filter(
            type=User.Types.DRIVER, driver_duty=True
        ).exclude(
            Q(driver_trips__status__in=active_trip_statuses)
        ).distinct()

        if cab_class_id:
            drivers_without_active_trips = drivers_without_active_trips.filter(vehicles__cab_class__id=cab_class_id)

        nearby_drivers = []

        for driver in drivers_without_active_trips:
            try:
                subscription = Subscriptions.objects.filter(driver=driver, is_active=True, payment_status="PAID").first()
                # if subscription and subscription.pending_rides > 0:
                if subscription:
                    if not subscription.is_expired():
                        
                        location = driver.currentlocation
                        distance = haversine(float(latitude), float(longitude), float(location.current_latitude), float(location.current_longitude))
                        print("driver", driver.phone, "distance:", distance, " <=",  max_distance)
                        if distance <= max_distance:
                            print(1)
                            nearby_drivers.append(driver)
                # else:
                #     raise NotFound(detail="Subscription not found, Please Subscribe fast")
                    
            except CurrentLocation.DoesNotExist as e:
                logger.error(f"Error occurred: {e}")
                continue
            except Subscriptions.DoesNotExist as e:
                logger.error(f"Error occurred: {e}")
                raise NotFound(detail="Subscription not found, Please Subscribe fast")
                    

        serializer = NearestDriverSerializer(nearby_drivers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
