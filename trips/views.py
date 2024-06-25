from django.shortcuts import render
from rest_framework import generics, permissions, status
from trips.models import *
from trips import serializers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from admin_api.serializers import FeedbackSettingSerializer
from admin_api.models import FeedbackSetting
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