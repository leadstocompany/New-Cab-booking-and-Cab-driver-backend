from rest_framework import serializers
from cabs.models import *

class CabTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CabType
        fields = ('id', 'cab_type')

class CabClassSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CabClass
        fields = ['id', 'cab_type', 'cab_class', 'icon']
    
    def to_representation(self, instance):
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        return super(CabClassSerializer, self).to_representation(instance)

class VehicleLocationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = ['id', 'last_location','updated_at']


class VehicleMakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMaker
        fields = ['id', 'maker', 'cab_type']
    def to_representation(self, instance):
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        return super(VehicleMakerSerializer, self).to_representation(instance)

class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = ['id', 'maker', 'model']
    
    def to_representation(self, instance):
        self.fields['maker'] = VehicleMakerSerializer(read_only=True)
        return super(VehicleModelSerializer, self).to_representation(instance)

class VehicaleDetailsSerializer(serializers.ModelSerializer):
    driver = serializers.HiddenField(
    default=serializers.CurrentUserDefault())
    class Meta:
        model = Vehicle
        exclude = ['is_approved',]

    def to_representation(self, instance):
        self.fields['maker'] = VehicleMakerSerializer(read_only=True)
        self.fields['model'] = VehicleModelSerializer(read_only=True)
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        self.fields['cab_class'] = CabClassSerializer(read_only=True)
        return super(VehicaleDetailsSerializer, self).to_representation(instance)