from rest_framework import serializers
from django.db.models import Q
from datetime import datetime
from accounts.models import User
from trips.models import Trip, TripRating
from accounts.models import User, Driver, BankAccount
from accounts.serializers import BankAccountSerializer
from cabs.models import *
from admin_api.models import *
from cabs.serializers import *
from cabs.models import Vehicle
from accounts.serializers import DriverProfileSerializer
from trips.serializers import TripSerializer, TripRatingSerializer
from wallets.models import Wallet
from wallets.serializers import WalletSerializer
from subscriptions.models import Subscriptions, Subscription_Logs
from subscriptions.serializers import SubscriptionSerializer, SubscriptionsLogsSerializer
from django.db.models import Sum, F, FloatField
from django.utils import timezone
from django.db.models.functions import Cast
from admin_api.models import City
from utility.rating  import get_driver_rating 
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
        fields = ['id', 'cab_type', 'icon']
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
    # cab_type = VehicleTypeSerializer()
    cab_type_name = serializers.SerializerMethodField()

    class Meta:
        model = VehicleMaker
        # fields = '__all__'
        fields = ['id', 'maker', 'cab_type','cab_type_name', 'is_active', 'icon']
        # fields = ['id', 'maker', 'is_active', 'icon']
    def validate(self, data):
        # Check if a car with the same name already exists
        maker = data.get('maker')
        existing_maker =  VehicleMaker.objects.filter(maker=maker).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_maker:
            raise serializers.ValidationError(f'A vehicle Maker with the name "{ maker }" already exists.')

        return data
    def get_cab_type_name(self, obj):
        return obj.cab_type.cab_type
    # cab_type
    # def to_representation(self, instance):
    #     self.fields['cab_type'] = VehicleTypeSerializer(read_only=True)
    #     return super(VehicleMakerSerializers, self).to_representation(instance)

       


class SaveVehicleModelSerializer(serializers.ModelSerializer):

    cabtype_name = serializers.SerializerMethodField()
    cabclass_name= serializers.SerializerMethodField()
    maker_name = serializers.SerializerMethodField()
    cabtype_icon = serializers.SerializerMethodField()
    cabclass_icon= serializers.SerializerMethodField()
    maker_icon = serializers.SerializerMethodField()
    class Meta:
        model = VehicleModel
        # fields="__all__"
        fields = ['id', 'model','cabtype','cabtype_name','cabtype_icon', 'cabclass','cabclass_name', 'cabclass_icon', 'maker','maker_name','maker_icon', 'model_image', 'is_active']
    # def get_maker_name(self, obj):
    #     return obj.maker.maker
    def validate(self, data):
        # Check if a car with the same name already exists
        model = data.get('model')
        existing_model =  VehicleModel.objects.filter(model=model).exclude(pk=self.instance.pk if self.instance else None).first()

        if existing_model:
            raise serializers.ValidationError(f'A vehicle Model with the name "{ model }" already exists.')

        return data
    def get_cabtype_name(self, obj):
        return obj.cabtype.cab_type
    def get_cabtype_icon(self, obj):
        return obj.cabtype.icon
    def get_cabclass_name(self, obj):
        return obj.cabclass.cab_class
    def get_cabclass_icon(self, obj):
        return obj.cabclass.icon
    def get_maker_name(self, obj):
        return obj.maker.maker
    
    def get_maker_icon(self, obj):
        return obj.maker.icon
    # def to_representation(self, instance):
    #     self.fields['cabtype'] = CabTypeSerializer(read_only=True)
    #     self.fields['cabclass'] = CabClassSerializer(read_only=True)
    #     self.fields['maker'] = VehicleMakerSerializers(read_only=True)
    #     return super(SaveVehicleModelSerializer, self).to_representation(instance)
    


class VehicleCertificateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCertificateField
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
    def create(self, validated_data):
        validated_data = self._get_set_cab_class(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._get_set_cab_class(validated_data)
        return super().update(instance, validated_data)
    def to_representation(self, instance):
       
        self.fields['driver'] = DriverProfileSerializer(read_only=True)
        self.fields['maker'] = VehicleMakerSerializer(read_only=True)
        self.fields['model'] = VehicleModelSerializer(read_only=True)
        self.fields['cab_type'] = CabTypeSerializer(read_only=True)
        self.fields['cab_class'] = CabClassSerializer(read_only=True)
        return super(VehicleSerializer, self).to_representation(instance)

    def _get_set_cab_class(self, validated_data):
        cab_type_id = validated_data.get('cab_type').id
        cab_type_obj=CabType.objects.get(id=cab_type_id)
        cabtype_name=cab_type_obj.cab_type
        cabClass=None 
        if cabtype_name == "Bick":
            if CabClass.objects.filter(cab_class="Bick").exists():
                cabClass=CabClass.objects.filter(cab_class="Bick", cab_type=validated_data.get('cab_type')).first()
          
        elif cabtype_name == "Auto":
            if CabClass.objects.filter(cab_class="Auto").exists():
                cabClass=CabClass.objects.filter(cab_class="Auto",cab_type=validated_data.get('cab_type')).first()
          
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
       

class DriverProfileVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
    
    def to_representation(self, instance):
        self.fields['model'] = VehicleModelSerializer(read_only=True)
        return super(DriverProfileVehicleSerializer, self).to_representation(instance)


class UserDocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocumentField
        fields = '__all__'


class FeedbackSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSetting
        fields = '__all__'


class DriverFeedbackPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverFeedbackPage
        fields = '__all__'



class VehiclePhotoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePhotoPage
        fields = '__all__'

# class DriverProfileCreateSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         lower_email = value.lower()
#         if User.objects.filter(email__iexact=lower_email).exists():
#             raise serializers.ValidationError("Email ID already used!")
#         return lower_email

#     class Meta:
#         model = Driver
#         fields = ('id','first_name', 'last_name', 'phone', 'email', 'full_address', 'pincode',
#                     'state', 'city', 'house_or_building', 'road_or_area', 'alternate_number','user_doc',
#                     'photo_upload', 'terms_policy', 'myride_insurance', 'latitude', 'longitude', 'profile_status',)


class DriverProfileCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    phone = serializers.CharField()

    def validate_email(self, value):
        lower_email = value.lower()
        if self.instance:
            instance=self.instance
            if User.objects.filter(email__iexact=lower_email).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("Email ID already used!")
        else:
            if User.objects.filter(email__iexact=lower_email).exists():
                raise serializers.ValidationError("Email ID already used!")
        return lower_email

    def validate_phone(self, value):
        # Ensure that the phone number is unique
        if self.instance:
            instance=self.instance
            if User.objects.filter(phone=value).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("Phone number already used!")
        else:
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("Phone number already used!")

        return value

    class Meta:
        model = Driver
        fields = (
            'id', 'first_name', 'last_name', 'phone', 'email', 'full_address', 'pincode',
            'state', 'city', 'house_or_building', 'road_or_area', 'alternate_number', 'user_doc',
            'photo_upload', 'terms_policy', 'myride_insurance', 'latitude', 'longitude', 'profile_status',
        )
        
class DriverListSerializer(serializers.ModelSerializer):
    vehicle_class = serializers.SerializerMethodField()
    rides_status= serializers.SerializerMethodField()
    class Meta:
        model = Driver
        fields = ('id','first_name', 'last_name', 'phone', 'email',  'pincode',
                    'state', 'city','photo_upload', 'myride_insurance', 'date_joined', 
                    'driver_duty', "profile_status", 'vehicle_class', "rides_status")
    def get_vehicle_class(self, obj):
        driver_id= obj.id
        vehicle = Vehicle.objects.filter(driver_id=driver_id).first()
        if vehicle and vehicle.cab_class:
            return vehicle.cab_class.cab_class
        return None 
        
        
    def get_rides_status(self, obj):
        if obj.profile_status in ["Approve"]:
            if obj.driver_trips.filter(Q(status='ON_TRIP') | Q(status='BOOKED'), Q(scheduled_datetime__isnull=True)).exists():
                rides_status={
                    "status": "On_Trip"
                }
            elif obj.driver_trips.filter(Q(status='ON_TRIP') & Q(scheduled_datetime__isnull=False)).exists():
                schedule_trip_count=obj.driver_trips.filter(status='BOOKED', scheduled_datetime__isnull=False).count()
                rides_status={
                    "status": "On_Trip",
                    "schedule_trip_count": schedule_trip_count,
                }
            elif obj.driver_trips.filter(Q(status='BOOKED') & Q(scheduled_datetime__isnull=False)).exists():
                schedule_trip_count=obj.driver_trips.filter(status='BOOKED', scheduled_datetime__isnull=False).count()
                rides_status={
                    "status": "Avalable",
                    "schedule_trip_count": schedule_trip_count,
                }
            else:
                rides_status={
                    "status": "Avalable",
                }
        else:
              rides_status={
                    "status": "Not-Avalable",
                }
        return rides_status



class DriverDetailsSerializer(serializers.ModelSerializer):
    vehicle = serializers.SerializerMethodField()  # Nested vehicles
    ride_history=serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    bank_account = serializers.SerializerMethodField()
    subscription_details = serializers.SerializerMethodField()
    active_rides_details= serializers.SerializerMethodField()
    trip_rating_feedback=serializers.SerializerMethodField()
    rating=serializers.SerializerMethodField()
    class Meta:
        model = Driver
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'full_address', 'pincode',
                    'country','state', 'city', 'house_or_building', 'road_or_area', 'landmark','alternate_number','user_doc',
                    'photo_upload', 'terms_policy', 'myride_insurance', 'latitude', 'longitude', 'date_joined','driver_duty', "profile_status",'vehicle', 'ride_history', 'wallet',
                    'bank_account', 'subscription_details', 'active_rides_details', 'trip_rating_feedback', 'rating')
   
    def get_vehicle(self, obj):
        driver_id = obj.id  # Assuming the related name is 'vehicles'
        vehicle=Vehicle.objects.filter(driver_id=driver_id).first()
        if vehicle and vehicle.cab_class:
            vehicle_class_id= vehicle.cab_class.id
            cabbookingprice=CabBookingPrice.objects.filter(cab_class_id=vehicle_class_id).first()
         # Retrieve the base fare or set a default value if cabbookingprice is not found
            price_per_km = cabbookingprice.base_fare if cabbookingprice else 0
        else:
            price_per_km=0
        
        # Serialize the vehicle data
        vehicle_data = DriverProfileVehicleSerializer(vehicle).data
        
        # Add the custom field to the serialized data
        vehicle_data['price_per_km'] = price_per_km
        return vehicle_data 

    def get_ride_history(self, obj):
       # Assuming the related name is 'trips'
        driver_id = obj.id  # Assuming the related name is 'vehicles'
        trips=Trip.objects.filter(driver_id=driver_id, status='COMPLETED').order_by('-created_at')
        total_rides = Trip.objects.filter(driver_id=driver_id, status='COMPLETED').count()
        total_km=Trip.objects.filter(driver_id=driver_id, status='COMPLETED').aggregate(total_distance=Sum(Cast('distance', FloatField())))['total_distance']
        # today = timezone.now().date()
        today = timezone.localtime().date()
        current_rides= Trip.objects.filter(driver_id=driver_id, status='COMPLETED', created_at__date=today).count()
        scheduled_rides=Trip.objects.filter(driver_id=driver_id, status='BOOKED', scheduled_datetime__isnull=False).count()
        total_earning=Trip.objects.filter(driver_id=driver_id, status='COMPLETED',payment_status = 'paid').aggregate(total_fare_sum=Sum('total_fare'))['total_fare_sum']
        ride_history={
            "total_rides": total_rides,
            "total_km":total_km,
            "current_rides":current_rides,
            "scheduled_rides":scheduled_rides,
            "total_earning":total_earning,
            "trips":TripSerializer(trips, many=True).data

        }
        return ride_history
    def get_wallet(self, obj):
        driver_id = obj.id  # Assuming the related name is 'vehicles'
        wallet=Wallet.objects.filter(user__id=driver_id).first()
        return WalletSerializer(wallet).data
    def get_bank_account(self, obj):
        driver_id = obj.id 
        bank_account=BankAccount.objects.filter(driver__id=driver_id).first()
        
        return BankAccountSerializer(bank_account).data
    def get_subscription_details(self, obj):
        driver_id=obj.id
        subscription=Subscriptions.objects.filter(driver__id=driver_id).first()
        subscription_log=Subscription_Logs.objects.filter(driver__id=driver_id).order_by('-created_at')
        subscription_details={
            "subscription_data":SubscriptionSerializer(subscription).data,
            "subscription_log_data":SubscriptionsLogsSerializer(subscription_log, many=True).data
        }
        return subscription_details
    def get_active_rides_details(self, obj):
        driver_id=obj.id
        scheduled_rides=Trip.objects.filter(driver_id=driver_id, status='BOOKED', scheduled_datetime__isnull=False).order_by('-created_at')
        current_ride= Trip.objects.filter(driver_id=driver_id, status='ON_TRIP').first()
        active_rides_details={
            'scheduled_ride':TripSerializer(scheduled_rides, many=True).data,
            'current_ride': TripSerializer(current_ride).data if current_ride else None
        }
        return active_rides_details
   
    def get_trip_rating_feedback(self, obj):
        print(obj.id, "id")
        driver_trip_rating = TripRating.objects.filter(driver_id=obj.id).order_by('-created_at')
        return TripRatingSerializer(driver_trip_rating, many=True).data  # Ensure to return .data for the serialized result

    def get_rating(self, obj):
        driver_id = obj.id
        driver=Driver.objects.get(id=driver_id) 
        rating=get_driver_rating(driver)
        return rating

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'city_name']