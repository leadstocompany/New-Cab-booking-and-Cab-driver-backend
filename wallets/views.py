from django.shortcuts import render

# Create your views here.
# views.py

import stripe
from JLP_MyRide import settings
from accounts.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if Wallet.objects.filter(user=user).exists():
            return Response({'error': 'Wallet already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = Wallet.objects.create(user=user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class GetWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            wallet = Wallet.objects.get(user=user)
            profile = User.objects.get(user=user)
            user_type = profile.user_type
            now = timezone.now()
            wallet_serializer=WalletSerializer(wallet)
            # Define the start and end of today
            start_of_today = timezone.make_aware(datetime.combine(now.date(), time.min))
            end_of_today = timezone.make_aware(datetime.combine(now.date(), time.max))
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'User profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if user_type == 'customer':
            # Calculate total expenses for customers
            total_expenses = self.calculate_total_expenses(user)
            transection=Transaction.objects.filter( user=user,date__range=(start_of_today, end_of_today))
            transection_serializer=TransactionSerializer(today_payments, many=True)
            data = {
                "wallet": wallet_serializer.data,
                'total_expenses': total_expenses,
                "transection":transection_serializer.data,
            }
        else:
            # Filter transactions that are of type "DEPOSIT" and created today
            today_payments = Transaction.objects.filter( user=user,
                transaction_type="DEPOSIT",
                date__range=(start_of_today, end_of_today)
            )
            today_payments_serializer=TransactionSerializer(today_payments, many=True)
            today_total_payment_amount = Transaction.objects.filter(user=user,transaction_type="DEPOSIT", date__range=(start_of_today, end_of_today)).aggregate(total_amount=Sum('amount'))['total_amount'] or 0.00

            data = {
                "wallet": wallet_serializer.data,
                "today_payments":today_payments_serializer.data,
                "today_total_payment_amount":today_total_payment_amount
            }
        
        return Response(data, status=status.HTTP_200_OK)

    def calculate_total_withdrawn(self, user):
        total_withdrawn = Transaction.objects.filter(
            user=user,
            transaction_type='WITHDRAW'
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0.00

        return total_withdrawn




class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        token = request.data.get('token')

        if not amount or not token:
            return Response({'error': 'Amount and token are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            charge = stripe.Charge.create(
                amount=int(float(amount) * 100),  # Amount in cents
                currency='usd',
                description='Wallet Deposit',
                source=token
            )
            if Wallet.objects.filter(user=request.user).exists():
                wallet=Wallet.objects.filter(user=request.user).first()
            else:
                wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += float(amount)
            wallet.save()

            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='DEPOSIT',
                remake='Stripe deposit'
            )

            return Response({'success': 'Deposit successful'}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        destination_account = request.data.get('destination_account')

        if not amount or not destination_account:
            return Response({'error': 'Amount and destination account are required'}, status=status.HTTP_400_BAD_REQUEST)

        if Wallet.objects.filter(user=request.user).exists():
            wallet=Wallet.objects.filter(user=request.user).first()
        else:
            wallet, created = Wallet.objects.get_or_create(user=request.user)

        if wallet.balance < float(amount):
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Simulate a withdrawal by creating a Transfer
            transfer = stripe.Transfer.create(
                amount=int(float(amount) * 100),  # Amount in cents
                currency='usd',
                destination=destination_account,
                description='Wallet Withdrawal'
            )

            wallet.balance -= float(amount)
            wallet.save()

            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='WITHDRAW',
                remark='Stripe withdrawal'
            )

            return Response({'success': 'Withdrawal successful'}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GetTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = User.objects.get(user=user)
            user_type = profile.user_type
                   
        except User.DoesNotExist:
            return Response({'error': 'User profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if user_type == 'customer':
            # Calculate total expenses for customers   
            deposit = Transaction.objects.filter(user=user,transaction_type="DEPOSIT")
            deposit_serializer=TransactionSerializer(deposit, many=True)
            expense= Transaction.objects.filter(user=user,transaction_type="WITHDRAW")
            expense_serializer=TransactionSerializer(expense, many=True)
            data = {
                'expenses': expense_serializer.data,
                "deposit":deposit_serializer.data,
            }
        else:
            # Filter transactions that are of type "DEPOSIT" and created today
            payments = Transaction.objects.filter(user=user,transaction_type="DEPOSIT")
            payments_serializer=TransactionSerializer(payments, many=True)
            withdraw = Transaction.objects.filter(user=user,transaction_type="WITHDRAW")
            withdraw_serializer=TransactionSerializer(withdraw, many=True)

            data = {
                "payments":payments_serializer.data,
                "withdraw":withdraw_serializer.data
            }
        
        return Response(data, status=status.HTTP_200_OK)
