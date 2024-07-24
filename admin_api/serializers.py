from rest_framework import serializers
from django.db.models import Q
from datetime import datetime
from accounts.models import User
from trips.models import Trip
from accounts.models import User, Driver
from cabs.models import *
from admin_api.models import *

class AdminLoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)
        if not User.objects.filter(Q(email = username) | Q(phone= username),is_superuser=1).exists():
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        user = authenticate(username=username, password=password)
        print(user, "user")
        if user is None:

            raise serializers.ValidationError (
            "A user with this email and password is not found."
            
            )
        try:
            return {
                "user_phone":user.phone,
            }

        except user.DoesNotExist:
            raise serializers.ValidationError(
                "User with given email/Phone and password does not exists", 
            )
def authenticate(username=None, password=None, **kwargs):
    try:
        user=User.objects.get(Q(email = username) | Q(phone = username))
    except User.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None
class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'full_address', 'photo_upload']

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CabType
        fields = ['id', 'cab_type']
    def validate(self, data):
        # Check if a car with the same name already exists
        cab_type = data.get('cab_type')
        existing_cabtype =  CabType.objects.filter(cab_type=cab_type).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_cabtype:
            raise serializers.ValidationError(f'A vehicle type with the name "{ cab_type }" already exists.')

        return data




class SaveVehicleClassSerializer(serializers.ModelSerializer):
    cab_type_name = serializers.SerializerMethodField()
    class Meta:
        model = CabClass
        fields = ['id', 'cab_class', 'icon','cab_type', 'cab_type_name', 'is_active']
    def validate(self, data):
        # Check if a car with the same name already exists
        cab_class = data.get('cab_class')
        existing_cabclass =  CabClass.objects.filter(cab_class=cab_class).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_cabclass:
            raise serializers.ValidationError(f'A cab class with the name "{ cab_class }" already exists.')

        return data
    def get_cab_type_name(self, obj):
        return obj.cab_type.cab_type
       
class VehicleMakerSerializers(serializers.ModelSerializer):
    # cab_type = serializers.SerializerMethodField()
    cab_type = VehicleTypeSerializer()

    class Meta:
        model = VehicleMaker
        # fields = '__all__'
        fields = ['id', 'maker', 'cab_type', 'is_active']
    def validate(self, data):
        # Check if a car with the same name already exists
        maker = data.get('maker')
        existing_maker =  VehicleMaker.objects.filter(maker=maker).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_maker:
            raise serializers.ValidationError(f'A vehicle Maker with the name "{ maker }" already exists.')

        return data
       


class SaveVehicleModelSerializer(serializers.ModelSerializer):
    maker_name = VehicleMakerSerializers()
    class Meta:
        model = VehicleModel
        # fields="__all__"
        fields = ['id', 'model', 'maker','model_image', 'is_active']
    # def get_maker_name(self, obj):
    #     return obj.maker.maker
    def validate(self, data):
        # Check if a car with the same name already exists
        model = data.get('model')
        existing_model =  VehicleModel.objects.filter(model=model).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_model:
            raise serializers.ValidationError(f'A vehicle Model with the name "{ model }" already exists.')

        return data
    


class VehicleCertificateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCertificateField
        fields = '__all__'



class UserDocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocumentField
        fields = '__all__'


class FeedbackSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSetting
        fields = '__all__'
