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
        fields = ('id','first_name', 'last_name', 'phone', 'email', 'birth_day', 'gender', 'photo_upload', 'type')

class TransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'transaction_type','transaction_mode', 'date', 'remark']


class IncomeTransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    sender = UserProfileSerializer()
    class Meta:
        model = Transaction
        fields = ['user','sender',  'amount', 'transaction_type','transaction_mode', 'date', 'remark']

class ExpenseTransactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    receiver = UserProfileSerializer()
    class Meta:
        model = Transaction
        fields = ['user', 'receiver', 'amount', 'transaction_type','transaction_mode', 'date', 'remark']




class WalletSerializer(serializers.ModelSerializer):
    # total_expenses = serializers.SerializerMethodField(read_only=True)  # Ensuring read-only
    user = UserProfileSerializer()

    class Meta:
        model = Wallet
        fields = ['id','user', 'balance']

    # def get_total_expenses(self, obj):
    #     user = obj.user
    #     print(user.id, "id", user.type)
    #     # Check if the user is of type 'customer'
    #     if user.type == 'CUSTOMER':
    #         total_withdrawn = Transaction.objects.filter(
    #             user=user,
    #             transaction_type='WITHDRAW'
    #         ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0.00
            
    #         return total_withdrawn
        
    #     return None  # Returning None for non-customer users
    # 'total_expenses'