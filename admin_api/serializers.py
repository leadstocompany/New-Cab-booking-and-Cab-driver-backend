from rest_framework import serializers
from django.db.models import Q
from datetime import datetime
from accounts.models import User
from trips.models import Trip
from accounts.models import User, Driver
from cabs.models import *
from admin_api.models import *
from cabs.serializers import *
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
    # cab_type = VehicleTypeSerializer()

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
    def to_representation(self, instance):
        self.fields['cab_type'] = VehicleTypeSerializer(read_only=True)
        return super(VehicleMakerSerializers, self).to_representation(instance)

       


class SaveVehicleModelSerializer(serializers.ModelSerializer):
    # maker_name = VehicleMakerSerializers()
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
    def to_representation(self, instance):
        self.fields['maker'] = VehicleMakerSerializers(read_only=True)
        return super(SaveVehicleModelSerializer, self).to_representation(instance)
    


class VehicleCertificateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCertificateField
        fields = '__all__'


class VehicaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        # exclude = ['is_approved',]
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
        return super(VehicaleSerializer, self).to_representation(instance)

    def _get_set_cab_class(self, validated_data):
        cab_type_id = validated_data.get('cab_type')
        cab_type_obj=CabType.objects.get(id=cab_type_id)
        cabtype_name=cab_type_obj.cab_type
        cab_class=None 
        economy=('Toyota Corolla', 'Honda Civic', 'Hyundai Elantra', 'Nissan Sentra', 'Mazda3', 'Honda Fit', 'Toyota Yaris',
 'Hyundai Accent', 'Kia Rio', 'Chevrolet Spark', 'Ford Fiesta', 'Volkswagen Golf', 'Honda Civic Hatchback', 'Toyota Prius C', 'Mini Cooper',
 'Chevrolet Cruze', 'Ford Focus', 'Kia Forte', 'Nissan Versa', 'Mitsubishi Mirage G4')
        sedans=('BMW 5 Series', 'Audi A6', 'Lexus ES', 'Jaguar XF', 'Chevrolet Impala', 'Chrysler 300',  'BMW 7 Series', 'Audi A8', 'Lexus LS',
'Toyota Avalon', 'Ford Taurus', 'Dodge Charger', 'BMW M3', 'Audi S4', 'Mercedes-AMG C63', 'Cadillac CTS-V', 'Alfa Romeo Giulia Quadrifoglio')
        confort=('Mercedes-Benz S-Class', 'BMW 7 Series', 'Audi A8', 'Lexus LS', 'Genesis G90', 'Mercedes-Benz E-Class', 'BMW 5 Series', 
            'Audi A6', 'Lexus ES', 'Volvo S90', 'Cadillac Escalade', 'Lincoln Navigator', 'Mercedes-Benz GLS-Class', 'BMW X7', 
            'Range Rover', 'Lexus RX', 'Acura MDX', 'Audi Q7', 'BMW X5', 'Volvo XC90', 'Mazda CX-5', 'Honda CR-V', 'Toyota Highlander', 'Subaru Outback',
            'Kia TelluridePorsche Macan', 'Jaguar F-Pace', 'Audi Q5', 'Mercedes-Benz GLC', 'Lexus NX')
        taxi_5_seater=('Toyota Camry', 'Honda Accord', 'Hyundai Sonata', 'Nissan Altima', 'Ford Fusion', 'Toyota Corolla', 'Honda Civic', 'Hyundai Elantra', 
        'Nissan Sentra', 'Mazda3', 'Hybrid Models', 'Toyota Prius', 'Honda Insight', 'Ford Fusion Hybrid', 'Hyundai Ioniq', 'Toyota Camry Hybrid', 'Toyota RAV4', 'Honda CR-V',
        'Nissan Rogue', 'Hyundai Tucson', 'Mazda CX-5', 'Nissan Leaf', 'Chevrolet Bolt EV', 'Tesla Model 3', 'Hyundai Kona Electric', 'Kia Soul EV')
        taxi_7_seater=('Toyota Sienna', 'Honda Odyssey', 'Chrysler Pacifica', 'Kia Carnival', 'Dodge Grand Caravan', 'Toyota Highlander',
 'Honda Pilot', 'Ford ExplorerChevrolet Traverse','Hyundai Palisade', 'Volkswagen Sharan', 'Ford Galaxy',
 'Citroën Grand C4 SpaceTourer', 'Peugeot 5008', 'Kia SorentoMercedes-Benz V-Class', 'BMW X7', 'Audi Q7', 'Volvo XC90', 'Lexus RX L')
        if cabtype_name == "Bick":
            if CabClass.objects.filter(cab_class="Bick").exists():
                cabclass=CabClass.objects.filter(cab_class="Bick").first()
            else:
                cabclass=CabClass.objects.create(cab_class="Bick", cab_type=cab_type_obj)
            cab_class=cabclass
        elif cabtype_name == "Auto":
            if CabClass.objects.filter(cab_class="Auto").exists():
                cabclass=CabClass.objects.filter(cab_class="Auto").first()
            else:
                cabclass=CabClass.objects.create(cab_class="Auto", cab_type=cab_type_obj)
            cab_class=cabclass
        else:
            cabmodel_id=validated_data.get('cab_model')
            cabmodel_obj=VehicleModel.objects.get(id=cabmodel_id)
            cabmodel_name=cabmodel_obj.model
            if cabmodel_name in economy:
                vehicle_class_name="Economy"
            elif cabmodel_name in sedans:
                vehicle_class_name="Sedans"
            elif cabmodel_name in taxi_7_seater:
                vehicle_class_name="Taxi 7-seater"
            elif cabmodel_name in confort:
                vehicle_class_name="Confort"
            elif cabmodel_name in taxi_5_seater:
                vehicle_class_name="Taxi 5-seater"
            else:
                vehicle_class_name="Economy"
            cabclass=CabClass.objects.filter(cab_class=vehicle_class_name).first()
            cab_class=cabclass
        validated_data['cab_class'] = cab_class
        return validated_data
       



class UserDocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocumentField
        fields = '__all__'


class FeedbackSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSetting
        fields = '__all__'
