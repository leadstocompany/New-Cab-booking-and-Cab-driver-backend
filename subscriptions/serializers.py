from rest_framework import serializers
from .models import Subscription,  SubscriptionPlan, Subscriptions_Logs
from accounts.serializers import DriverProfileSerializer
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id','plan_name', 'ride_numbers', 'price', 'discount', 'original_price', 'is_active', "created_at", "updated_at"]



class SubscriptionSerializer(serializers.ModelSerializer):
    # plan = SubscriptionPlanSerializer()

    class Meta:
        model = Subscription
        fields = ['driver', 'plan', 'complated_rides', 'pending_rides', 'pay_amount', 'payment_status', 'number_of_time_subscribe', 'payment_id','created_at', 'updated_at', 'is_active']
    def to_representation(self, instance):
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['plan'] =  SubscriptionPlanSerializer(read_only=True)
        return super(SubscriptionSerializer, self).to_representation(instance)
    

class SubscriptionsLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions_Logs
        fields = ['driver', 'plan', 'pay_amount', 'payment_status',  'payment_id', 'created_at', 'updated_at', 'is_active']
    def to_representation(self, instance):
        self.fields['driver'] =  DriverProfileSerializer(read_only=True)
        self.fields['plan'] =  SubscriptionPlanSerializer(read_only=True)
        return super(SubscriptionSerializer, self).to_representation(instance)
    
