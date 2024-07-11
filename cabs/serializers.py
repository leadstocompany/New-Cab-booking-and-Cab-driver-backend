from rest_framework import serializers
from cabs.models import *
from accounts.serializers import DriverProfileSerializer, CurrentLocationSerializer
from accounts.models import User
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
        fields = ['id', 'last_latitude', 'last_longitude', 'updated_at']


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
       
class CabBookingPriceSerializer(serializers.ModelSerializer):
    cab_class = CabClassSerializer()
    class Meta:
        model = CabBookingPrice
        fields = '__all__'



class NearestDriverSerializer(serializers.ModelSerializer):
    vehicles = VehicaleDetailsSerializer(many=True, read_only=True)
    current_location = CurrentLocationSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'type', 'current_location', 'vehicles']

  