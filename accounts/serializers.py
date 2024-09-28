from rest_framework import serializers
from rest_framework.validators import UniqueValidator
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
    phone = serializers.CharField()

   
    def validate_email(self, value):
        lower_email = value.lower()
        
        # Get the current instance if it's provided (update scenario)
        instance = self.instance
        
        # Check if the email is already used by any other user except the current one
        if User.objects.filter(email__iexact=lower_email).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Email ID already used!")

        return lower_email
    
    def validate_phone(self, value):
        print(value)
        instance = self.instance
        # Ensure that the phone number is unique
        if User.objects.filter(phone=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Phone number already used!")
        return value

    class Meta:
        model = Driver
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'full_address', 'pincode',
                    'state', 'city', 'house_or_building', 'road_or_area', 'alternate_number','user_doc',
                    'photo_upload', 'terms_policy', 'myride_insurance', 'latitude', 'longitude', 'profile_status', 'rejection_reason', 'driver_duty')
        read_only_fields = ('profile_status', 'rejection_reason','driver_duty') 
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


# class BankAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BankAccount
#         fields = '__all__'

class BankAccountSerializer(serializers.ModelSerializer):
    # Adding unique validation on account_number and ifsc_code
    account_number = serializers.CharField(
        max_length=50, 
        validators=[UniqueValidator(queryset=BankAccount.objects.all(), message="Account number already exists!")]
    )
    swift_code = serializers.CharField(
        max_length=50, 
        validators=[UniqueValidator(queryset=BankAccount.objects.all(), message="IFSC code already exists!")]
    )

    class Meta:
        model = BankAccount
        fields = '__all__'

class CurrentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentLocation
        fields = ['current_latitude', 'current_longitude', 'timestamp']
        # read_only_fields = ['timestamp']



class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'birth_day', 'gender', 'photo_upload', 'type')
