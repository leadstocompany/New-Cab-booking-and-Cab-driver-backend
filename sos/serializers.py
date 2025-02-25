from rest_framework import serializers

from accounts.models import User
from .models import SOSHelpRequest, SOSMessage
from trips.serializers import TripSerializer
from accounts.serializers import UserProfileSerializer
from trips.serializers import TripSerializer
class SOSHelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSHelpRequest
        fields = ['id', 'user', 'trip', 'message', 'location','last_latitude', 'last_longitude', 'created_at', 'resolved']
    def to_representation(self, instance):
        self.fields['user'] =  UserProfileSerializer(read_only=True)
        self.fields['trip'] =  TripSerializer(read_only=True)
        return super(SOSHelpRequestSerializer, self).to_representation(instance)

class SOSMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSMessage
        fields = ['id',"message"]

class AllSOSMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSMessage      

class SOSHelpRequestListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.full_name')
    phone = serializers.CharField(source='user.phone')
    user_type = serializers.CharField(source='user.type')

    class Meta:
        model = SOSHelpRequest
        fields = ['id', 'name', 'phone', 'user_type', 'created_at']



class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone', 'email', 'type']

class DriverDetailSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.SerializerMethodField()
    vehicle_number = serializers.SerializerMethodField()
    vehicle_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone', 'type', 'vehicle_model', 'vehicle_number', 'vehicle_id']

    def get_vehicle_model(self, obj):
        vehicle = obj.vehicles.first()
        return vehicle.model.model if vehicle and vehicle.model else None

    def get_vehicle_number(self, obj):
        vehicle = obj.vehicles.first()
        return vehicle.number_plate if vehicle else None 

    def get_vehicle_id(self, obj):
        vehicle = obj.vehicles.first()
        return vehicle.id if vehicle else None



class SOSHelpRequestDetailSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer(source='user')
    driver_details = DriverDetailSerializer(source='trip.driver')
    ride_details = TripSerializer(source='trip')
    name = serializers.CharField(source='user.full_name')
    user_type = serializers.CharField(source='user.type')


    class Meta:
        model = SOSHelpRequest
        fields = ['id', 'name', 'user_type', 'message', 'location', 'last_latitude', 'last_longitude', 'created_at', 'resolved', 'customer', 'driver_details', 'ride_details']
