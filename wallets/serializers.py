# serializers.py

from rest_framework import serializers
from .models import Wallet, Transaction
from django.db.models import Sum
from accounts.models import User
# class WalletSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Wallet
#         fields = ['user', 'balance']

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', email', 'birth_day', 'gender', 'photo_upload', 'type')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user',  'transaction_type', 'date', 'remake']



