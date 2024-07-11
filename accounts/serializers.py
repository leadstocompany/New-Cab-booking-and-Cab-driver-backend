from rest_framework import serializers
from accounts.models import *
class UserAuthSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.filter(phone=data["phone"], is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data
class FileUploadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileUpload
        fields = ['file', 'phone']

class CustomerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        lower_email = value.lower()
        instance = self.instance

        queryset = Customer.objects.filter(email__iexact=lower_email).exclude(pk=instance.pk if instance else None)
        if queryset.exists():
            raise serializers.ValidationError("Email ID already used!")
        return lower_email
    class Meta:
        model = Customer
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'birth_day', 'gender', 'photo_upload')

# class DriverProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Driver
#         fields = '__all__'

class DriverProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email ID already used!")
        return lower_email

    class Meta:
        model = Driver
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'full_address', 'pincode',
                    'state', 'city', 'house_or_building', 'road_or_area', 'alternate_number','user_doc',
                    'photo_upload', 'terms_policy', 'myride_insurance')

class DriverResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confim_password = serializers.CharField(required=True)
    
    def validate(self, data):
        
        if data['password'] != data['confim_password']:
            raise serializers.ValidationError("password & confim_password are not same!")
        return data
    # class Meta:
    #     model = Driver
    #     fields = ('id','first_name', 'last_name', 'phone', 'email', 'password', 'confim_password')

    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data.get('password'))
    #     return super(UserSerializer, self).create(validated_data)


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class CurrentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentLocation
        fields = ['current_latitude', 'current_longitude', 'timestamp']
        # read_only_fields = ['timestamp']