from rest_framework import serializers
from .models import CustomerReferral, ReferralReward
from accounts.models import Customer
from wallets.models import Wallet

class ReferralRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralReward
        fields = ['id', 'title', 'referrer_reward_amount', 'referred_reward_amount']
