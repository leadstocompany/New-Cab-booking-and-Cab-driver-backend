

from rest_framework import serializers

from notifications.models import DriverNotification


class DriverNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverNotification
        fields = '__all__'