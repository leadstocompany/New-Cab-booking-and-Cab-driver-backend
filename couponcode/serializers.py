from rest_framework import serializers
from .models import Coupon


class ActiveCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'name', 'title', 'terms_conditions', 'code', 'discount', 'valid_from', 'valid_to']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['name', 'title', 'code', 'discount', 'valid_from', 'valid_to', 'active']
        read_only_fields = ['code']