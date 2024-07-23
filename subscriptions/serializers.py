from rest_framework import serializers
from .models import Subscription,  SubscriptionPlan, Subscriptions_Logs

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id','plan_name', 'ride_numbers', 'price', 'discount', 'original_price', 'is_active', "created_at", "updated_at"]



class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()

    class Meta:
        model = Subscription
        fields = ['driver', 'plan', 'complated_rides', 'pending_rides', 'pay_amount', 'payment_status', 'number_of_time_subscribe', 'payment_id','created_at', 'updated_at', 'is_active']

class SubscriptionsLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions_Logs
        fields = ['driver', 'plan', 'pay_amount', 'payment_status',  'payment_id', 'created_at', 'updated_at', 'is_active']