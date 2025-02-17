

from rest_framework import serializers

from notifications.models import DriverNotification


class DriverNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverNotification
        fields = '__all__'

class DriverNotificationRequestSerializer(serializers.ModelSerializer):
    banner = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = DriverNotification
        fields = '__all__'
