

from rest_framework import serializers

from notifications.models import DriverNotification


class DriverNotificationSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, read_only=True)
    class Meta:
        model = DriverNotification
        fields = '__all__'
        
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        # Force is_active to be True
        representation['is_active'] = True
        return representation

class DriverNotificationRequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DriverNotification
        fields = '__all__'
