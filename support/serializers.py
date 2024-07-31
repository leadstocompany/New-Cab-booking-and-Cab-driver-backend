from rest_framework import serializers
from .models import DriverSupport, CustomerSupport

class DriverSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverSupport
        fields = '__all__'

class CustomerSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSupport
        fields = '__all__'


