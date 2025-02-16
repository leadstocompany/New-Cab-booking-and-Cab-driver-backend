from rest_framework import serializers
from trips.models import *
from accounts.serializers import DriverProfileSerializer, CustomerProfileSerializer
from cabs.models import Vehicle
from cabs.serializers import CabClassSerializer

class CabSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vehicle
        fields = '__all__'
       
class TripSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Trip
        # fields = '__all__'
        fields = ['id','trip_id','customer','driver', 'cab','status','source','destination', 'distance', 'time', 'ride_type','otp_count', 'rent_price', 'scheduled_datetime', 'canceled_by', 'cancel_reason', 'otp', 'payment_type', 'waiting_time', 'waiting_charge', 'total_fare', 'payment_status',  'pickup_latitude','pickup_longitude','dropup_latitude','dropup_longitude', 'created_at']
    def to_representation(self, instance):
        self.fields['customer'] =  CustomerProfileSerializer(read_only=True)
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['cab'] =  CabSerializer(read_only=True)
        self.fields['ride_type'] = CabClassSerializer(read_only=True)
       
        return super(TripSerializer, self).to_representation(instance)

class TripRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TripRating
        # fields = '__all__'
        fields = ['id','feedbacksetting', 'customer','driver', 'trip', 'star', 'feedback' ]
    def to_representation(self, instance):
        self.fields['customer'] =  CustomerProfileSerializer(read_only=True)
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['trip'] =  TripSerializer(read_only=True)

        return super(TripRatingSerializer, self).to_representation(instance)

