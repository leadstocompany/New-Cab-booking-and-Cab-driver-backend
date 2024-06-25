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
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'birth_day', 'gender', 'photo_upload')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'transaction_type', 'date', 'remake']



class WalletSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    user=UserProfileSerializer()
    class Meta:
        model = Wallet
        fields = ['user', 'balance', 'total_expenses']

    def get_total_expenses(self, obj):
        request = self.context.get('request')
        user = request.user
        
        if hasattr(user, 'profile') and user.profile.user_type == 'customer':
            total_withdrawn = Transaction.objects.filter(
                user=user,
                transaction_type='WITHDRAW'
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0.00
            
            return total_withdrawn
        
        return None