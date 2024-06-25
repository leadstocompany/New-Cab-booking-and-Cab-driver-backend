from rest_framework import serializers
from trips.models import *

class TripSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Trip
        fields = '__all__'

class TripRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TripRating
        fields = '__all__'

class DriverPricingRatioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DriverPricingRatio
        fields = '__all__'
