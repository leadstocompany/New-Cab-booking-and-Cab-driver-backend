from rest_framework import serializers
from .models import Coupon,  CouponUsage
from accounts.models import User
from wallets.serializers import UserProfileSerializer
class ActiveCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'name', 'title', 'terms_conditions', 'code', 'discount', 'valid_from', 'valid_to']

# class CouponSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Coupon
#         fields = ['id', 'name', 'title','terms_conditions', 'code', 'discount', 'valid_from', 'valid_to', 'active']
#         read_only_fields = ['code']

# class UserProfileSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = User
#         fields = ('id','first_name', 'last_name', 'phone', 'email',  'gender', 'photo_upload')

class CouponUsageSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    coupon=CouponSerializer()
    class Meta:
        model = CouponUsage
        fields = ['id','user', 'coupon','used_at']