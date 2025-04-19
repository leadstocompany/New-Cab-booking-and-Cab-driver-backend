from rest_framework import serializers
from .models import Subscriptions,  SubscriptionPlan, Subscription_Logs
from accounts.serializers import DriverProfileSerializer
from trips.serializers import CabClassSerializer
# class SubscriptionPlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SubscriptionPlan
#         fields = ['id','plan_name', 'ride_numbers', 'price', 'discount', 'original_price', 'is_active', "created_at", "updated_at"]

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

    # def validate_vehicle_class(self, value):
    #     if SubscriptionPlan.objects.filter(vehicle_class=value).exists():
    #         raise serializers.ValidationError("A subscription plan for this vehicle class already exists.")
    #     return value
    def validate(self, attrs):
        vehicle_class = attrs.get('vehicle_class')
        plan_name = attrs.get('plan_name')

        if SubscriptionPlan.objects.filter(vehicle_class=vehicle_class, plan_name=plan_name).exists():
            raise serializers.ValidationError(
                "A subscription plan with this vehicle class and plan name already exists."
            )

        return attrs
    def to_representation(self, instance):
        self.fields['vehicle_class'] =  CabClassSerializer(read_only=True)
       
        return super(SubscriptionPlanSerializer, self).to_representation(instance)
    

class SubscriptionSerializer(serializers.ModelSerializer):
    # plan = SubscriptionPlanSerializer()

    class Meta:
        model = Subscriptions
        fields = ['driver', 'plan',  'pay_amount', 'payment_status', 'number_of_time_subscribe', 'payment_id','created_at', 'is_active', 'subcribe_date', 'expire_date']
        
    def to_representation(self, instance):
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['plan'] =  SubscriptionPlanSerializer(read_only=True)
        return super(SubscriptionSerializer, self).to_representation(instance)
    

class SubscriptionsLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription_Logs
        
        fields = ['driver', 'plan', 'pay_amount', 'payment_status', 'payment_id', 'created_at', 'is_active', 'subcribe_date', 'expire_date']
    def to_representation(self, instance):
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['plan'] =  SubscriptionPlanSerializer(read_only=True)
        return super(SubscriptionsLogsSerializer, self).to_representation(instance)
    
