from rest_framework import serializers
from .models import SOSHelpRequest

class SOSHelpRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSHelpRequest
        fields = ['id', 'user', 'trp', 'message, , 'created_at', 'resolved']
