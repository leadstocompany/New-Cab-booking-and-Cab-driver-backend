from django.shortcuts import render
from rest_framework import generics, permissions, status
from cabs.models import *
from cabs import serializers
# Create your views here.

class CabTypeAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.CabTypeSerializer
    queryset = CabType.objects.filter(is_active=True)

class CabClassAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.CabClassSerializer
    def get_queryset(self):
        return CabClass.objects.filter(cab_type=self.kwargs.get("pk"), is_active=True)

class VehicleMakerAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.VehicleMakerSerializer
    def get_queryset(self):
        return VehicleMaker.objects.filter(cab_type=self.kwargs.get("pk"), is_active=True)

class VehicleModelAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.VehicleModelSerializer
    def get_queryset(self):
        return VehicleModel.objects.filter(maker_id=self.kwargs.get("pk"), is_active=True)

class VehicleLocationUpdateAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.VehicleLocationUpdateSerializer
    def get_queryset(self):
        return Vehicle.objects.filter(pk=self.kwargs.get("pk"), is_active=True)

class VehicaleDetailsAPI(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.VehicaleDetailsSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(driver=self.request.user, is_active=True)

class GetVehicaleDetailsAPI(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    # permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.VehicaleDetailsSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(pk=self.kwargs.get("pk"), is_active=True)