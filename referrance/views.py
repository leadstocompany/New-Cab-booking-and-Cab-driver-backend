from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, parsers, permissions, status, views
from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import NotFound
from referrance.models import CustomerReferral, ReferralReward
from referrance.serializers import ReferralRewardSerializer
from accounts.models import Customer
from wallets.models import Wallet



class ApplyReferralCodeEarnRewardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        referrence_code = request.data.get("referrence_code")
        if referrence_code:
            try:
                referrer = Customer.objects.get(code=referrence_code)
            except Customer.DoesNotExist:
                return Response({"error": "Invalid referral code."}, status=status.HTTP_400_BAD_REQUEST)
            referred = request.user
            if referrer == referred:
                return Response({"error": "You cannot refer yourself."}, status=status.HTTP_400_BAD_REQUEST)
             # Check if the referral already exists
            if CustomerReferral.objects.filter(referrer=referrer, referred=referred).exists() or CustomerReferral.objects.filter(referred=referred).exists():
                return Response({"error": "Referral already used."}, status=status.HTTP_400_BAD_REQUEST)
            reward = ReferralReward.objects.first()
            referral = CustomerReferral.objects.create(referrer=referrer, referred=referred, referrer_reward_amount=reward.referrer_reward_amount, referred_reward_amount=reward.referred_reward_amount)
            referrer_wallet= Wallet.objects.filter(user=referrer).first()
            referrer_wallet.balance += reward.referrer_reward_amount
            referrer_wallet.save()
            referred_wallet=Wallet.objects.filter(user=referred).first()
            referred_wallet.balance += reward.referred_reward_amount
            referred_wallet.save()
            return Response({"message": "Referral code applied successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "referrence code field required."}, status=status.HTTP_400_BAD_REQUEST)
            
     



class ReferralRewardCreateOrUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # Check if a ReferralReward instance already exists
        try:
            referral_reward = ReferralReward.objects.get()
            # If an instance exists, update it
            serializer = ReferralRewardSerializer(referral_reward, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "ReferralReward updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ReferralReward.DoesNotExist:
            # If no instance exists, create a new one
            serializer = ReferralRewardSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "ReferralReward created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReferralRewardDetailView(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ReferralReward.objects.all()
    serializer_class = ReferralRewardSerializer

    def get_object(self):
        # Ensure that only one ReferralReward instance is fetched (or return 404 if none exist)
        try:
            return ReferralReward.objects.get()
        except ReferralReward.DoesNotExist:
            raise NotFound("ReferralReward instance does not exist.")
    
    # Optionally, you can override update and delete methods if custom behavior is needed
    def update(self, request, *args, **kwargs):
        referral_reward = self.get_object()
        serializer = self.get_serializer(referral_reward, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "ReferralReward updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  
class ReferralRewardDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        try:
            referral_reward = ReferralReward.objects.get(pk=pk)
            referral_reward.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ReferralReward.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)