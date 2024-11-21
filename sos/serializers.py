from rest_framework import serializers
from .models import SOSHelpRequest
from trips.serializers import TripSerializer
from accounts.serializers import UserProfileSerializer
class SOSHelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSHelpRequest
        fields = ['id', 'user', 'trip', 'message', 'location','last_latitude', 'last_longitude', 'created_at', 'resolved']
    def to_representation(self, instance):
        self.fields['user'] =  UserProfileSerializer(read_only=True)
        self.fields['trip'] =  TripSerializer(read_only=True)
        return super(SOSHelpRequestSerializer, self).to_representation(instance)
