from rest_framework import serializers
from cabs.models import *
from accounts.serializers import DriverProfileSerializer, CurrentLocationSerializer
from accounts.models import User
class CabTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CabType
        fields = ('id', 'cab_type', 'icon')

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
        fields = ['id', 'last_latitude', 'last_longitude', 'updated_at']


class VehicleMakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMaker
        fields = ['id', 'maker', 'cab_type', 'icon']
        #fields = ['id', 'maker', 'icon']
    def to_representation(self, instance):
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        return super(VehicleMakerSerializer, self).to_representation(instance)

class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = ['id','cabtype','cabclass', 'maker', 'model', "model_image", "is_active"]
    
    def to_representation(self, instance):
        self.fields['cabtype'] = CabTypeSerializer(read_only=True)
        self.fields['cabclass'] = CabClassSerializer(read_only=True)
        self.fields['maker'] = VehicleMakerSerializer(read_only=True)
        return super(VehicleModelSerializer, self).to_representation(instance)



class VehicaleDetailsSerializer(serializers.ModelSerializer):
    driver = serializers.HiddenField(
    default=serializers.CurrentUserDefault())
    booking_price = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        exclude = ['is_approved',]
    
    def get_booking_price(self, obj):
        if obj.cab_class:
            booking_price = CabBookingPrice.objects.filter(cab_class=obj.cab_class).first()
            if booking_price:
                return CabBookingPriceSerializer(booking_price).data
        return None
    def create(self, validated_data):
        validated_data = self._get_set_cab_class(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._get_set_cab_class(validated_data)
        return super().update(instance, validated_data)
    def to_representation(self, instance):
        self.fields['maker'] = VehicleMakerSerializer(read_only=True)
        self.fields['model'] = VehicleModelSerializer(read_only=True)
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        self.fields['cab_class'] = CabClassSerializer(read_only=True)
        return super(VehicaleDetailsSerializer, self).to_representation(instance)

    def _get_set_cab_class(self, validated_data):
        cab_type_id = validated_data.get('cab_type').id
        print(cab_type_id,"cab_id")
        cab_type_obj=CabType.objects.get(id=cab_type_id)
        cabtype_name=cab_type_obj.cab_type
        cabClass=None 
#        
        if cabtype_name == "Bick":
            if CabClass.objects.filter(cab_class="Bick").exists():
                cabClass=CabClass.objects.filter(cab_class="Bick", cab_type=validated_data.get('cab_type')).first()
            # else:
            #     cabclass=CabClass.objects.create(cab_class="Bick", cab_type=cab_type_id)
            # cab_class=cabclass
        elif cabtype_name == "Auto":
            if CabClass.objects.filter(cab_class="Auto").exists():
                cabClass=CabClass.objects.filter(cab_class="Auto",cab_type=validated_data.get('cab_type')).first()
            # else:
            #     cabclass=CabClass.objects.create(cab_class="Auto", cab_type=cab_type_id)
            # cab_class=cabclass
        else:
           
            cabmodel_id=validated_data.get('model').id
            cabmodel_obj=VehicleModel.objects.get(id=cabmodel_id)
            cabmodel_name=cabmodel_obj.model
            AllvehicleClass=CabClass.objects.all()
            for cab_class in AllvehicleClass:
                cabModels_list=VehicleModel.objects.filter(cabclass=cab_class, cabtype=validated_data.get('cab_type'),maker=validated_data.get('maker'))
                # Get the list of IDs
                cabModels_ids = cabModels_list.values_list('id', flat=True)
                if cabmodel_id in cabModels_ids:
                    cabClass=cab_class
                    break


          
        validated_data['cab_class'] = cabClass
        return validated_data
       
class CabBookingPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CabBookingPrice
        fields = '__all__'

    def to_representation(self, instance):
        # Dynamically assign the nested serializer for cab_class
        self.fields['cab_class'] = CabClassSerializer(read_only=True)
        return super(CabBookingPriceSerializer, self).to_representation(instance)

    def validate(self, data):
        # Check if a CabBookingPrice already exists for the given cab_class
        cab_class = data.get('cab_class')
        if self.instance:  # If updating
            # Exclude the current instance from the unique check
            if CabBookingPrice.objects.filter(cab_class=cab_class).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This cab class already has a price entry.")
        else:  # If creating a new instance
            if CabBookingPrice.objects.filter(cab_class=cab_class).exists():
                raise serializers.ValidationError("This cab class already has a price entry.")
        return data


# class CabBookingPriceSerializer(serializers.ModelSerializer):
#     cab_class = CabClassSerializer(read_only=True)  # Nested serializer for cab_class

#     class Meta:
#         model = CabBookingPrice
#         fields = ['id', 'cab_class', 'base_fare', 'waiting_fare_per_minute']
#         unique_together = ['cab_class']  # Ensure unique constraint on cab_class

#     def to_representation(self, instance):
#         """Custom representation to ensure unique cab_class serialization."""
#         representation = super().to_representation(instance)
#         cab_class_id = instance.cab_class_id
#         # Add any custom logic to ensure cab_class uniqueness
#         representation['cab_class'] = {
#             'id': cab_class_id,
#             'name': instance.cab_class.cab_class  # Assuming 'name' is a field in CabClass
#         }
#         return representation
class NearestDriverSerializer(serializers.ModelSerializer):
    vehicles = VehicaleDetailsSerializer(many=True, read_only=True)
    current_location = CurrentLocationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'type', 'current_location', 'vehicles']

  