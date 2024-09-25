from django.shortcuts import render

# Create your views here.
# views.py

import stripe
from JLP_MyRide import settings
from accounts.models import User
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time
from utility.permissions import IsAdminOrSuperuser
from accounts.models import BankAccount
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if Wallet.objects.filter(user=user).exists():
            return Response({'error': 'Wallet already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        wallet = Wallet.objects.create(user=user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class GetWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        try:
            wallet = Wallet.objects.get(user=user)
            profile = User.objects.get(id=user.id)
            user_type = profile.type
            print("user type", user_type)
            now = timezone.now()
            wallet_serializer=WalletSerializer(wallet)
            # Define the start and end of today
            start_of_today = timezone.make_aware(datetime.combine(now.date(), time.min))
            end_of_today = timezone.make_aware(datetime.combine(now.date(), time.max))
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'User profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if user_type == 'CUSTOMER':
            # Calculate total expenses for customers
            total_expenses = self.calculate_total_withdrawn(user)
            transection=Transaction.objects.filter(user=user,date__range=(start_of_today, end_of_today))
            transection_serializer=TransactionSerializer(transection, many=True)
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




# class DepositView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         amount = request.data.get('amount')
#         token = request.data.get('token')

#         if not amount or not token:
#             return Response({'error': 'Amount and token are required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             charge = stripe.Charge.create(
#                 amount=int(float(amount) * 100),  # Amount in cents
#                 currency='usd',
#                 description='Wallet Deposit',
#                 source=token
#             )
#             if Wallet.objects.filter(user=request.user).exists():
#                 wallet=Wallet.objects.filter(user=request.user).first()
#             else:
#                 wallet, created = Wallet.objects.get_or_create(user=request.user)
#             wallet.balance += float(amount)
#             wallet.save()

#             Transaction.objects.create(
#                 user=request.user,
#                 amount=amount,
#                 transaction_type='DEPOSIT',
#                 remake='Stripe deposit'
#             )

#             return Response({'success': 'Deposit successful'}, status=status.HTTP_200_OK)
#         except stripe.error.StripeError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateWalletDepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')  # Amount in dollars (e.g., 50.00)

        if not amount or float(amount) <= 0:
            return Response({'error': 'Invalid deposit amount'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert the amount to cents, as Stripe works with the smallest currency unit
            amount_in_cents = int(float(amount) * 100)

            # Create a PaymentIntent for the wallet deposit
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='usd',  # Use the appropriate currency code (e.g., 'myr' for Malaysia)
                payment_method_types=['card'],  # Specify accepted payment methods
                description=f'Wallet deposit for {request.user.first_name}',
                metadata={'user_id': request.user.id},  # Add metadata for tracking
            )

            return Response({
                'client_secret': payment_intent.client_secret,  # Return this to frontend for confirming payment
                'payment_intent_id': payment_intent.id,
                "amount": amount
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while creating the payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SuccessWalletDepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_intent_id = request.data.get('payment_intent_id')
        amount = request.data.get('amount')

        if not payment_intent_id or not amount:
            return Response({'error': 'Payment intent ID and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the payment intent details from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Check if the payment was successful
            if payment_intent.status == 'succeeded':
                # Fetch or create the user's wallet
                wallet = Wallet.objects.filter(user=request.user).first()

                # Update the wallet balance
                wallet.balance += float(amount)
                wallet.save()

                # Log the deposit transaction
                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    remark=f'Stripe payment intent ID: {payment_intent.id}'
                )

                return Response({'success': 'Deposit successful', 'wallet_balance': wallet.balance}, status=status.HTTP_200_OK)
            else:
                return Response({'error': f'Payment not completed. Current status: {payment_intent.status}'}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while processing the payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        # destination_account = request.data.get('destination_account')
        driver_bank_account=BankAccount.objects.filter(driver=request.user).first()
        destination_account=driver_bank_account.account_id
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

            # Check the status of the transfer
            if transfer.status == 'paid':  # The transfer was successful
                # Update wallet balance
                wallet.balance -= float(amount)
                wallet.save()

                # Record the transaction in the database
                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='WITHDRAW',
                    remark=f'Stripe transfer ID: {transfer.id}'  # Save the transfer ID for reference
                )

                return Response({'success': 'Withdrawal successful', 'transfer_id': transfer.id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Transfer failed', 'status': transfer.status}, status=status.HTTP_400_BAD_REQUEST)

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



class WalletListView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer



class UserTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAdminOrSuperuser]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        return Transaction.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        deposite = queryset.filter(transaction_type="DEPOSIT")
        withdraw = queryset.filter(transaction_type="WITHDRAW")

       
        date = self.request.query_params.get('date', None)
        if date:
            parsed_date = parse_date(date)
            if parsed_date:
                deposite = deposite.filter(date__date=parsed_date)
                withdraw = withdraw.filter(date__date=parsed_date)

        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            deposite = deposite.filter(date__date__range=[start_date, end_date])
            withdraw = withdraw.filter(date__date__range=[start_date, end_date])
        deposite_serializer = self.get_serializer(deposite, many=True)
        withdraw_serializer = self.get_serializer(withdraw, many=True)
        return Response({
            "deposite": deposite_serializer.data,
            "withdraw": withdraw_serializer.data
        }, status=status.HTTP_200_OK)





















# reference code 

# class AdminTransferToBankView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         amount = request.data.get('amount')
#         bank_account_token = request.data.get('bank_account_token')  # Token created by Stripe.js or client-side

#         if not amount or not bank_account_token:
#             return Response({'error': 'Amount and bank account token are required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Attach the bank account token to the admin's Stripe account
#             external_account = stripe.Account.create_external_account(
#                 "acct_ADMIN_ACCOUNT_ID",  # Replace with admin's Stripe account ID
#                 external_account=bank_account_token
#             )

#             # Create a transfer to the external bank account
#             transfer = stripe.Transfer.create(
#                 amount=int(float(amount) * 100),  # Convert to cents
#                 currency="usd",
#                 destination=external_account.id,  # External account ID (e.g., ba_xxxxxxxx for bank)
#                 description=f'Transfer to bank account for {request.user.username}'
#             )

#             return Response({'success': 'Transfer successful'}, status=status.HTTP_200_OK)
        
#         except stripe.error.StripeError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': 'An error occurred during transfer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class WalletListView(generics.ListAPIView):
#     permission_classes = [IsAdminOrSuperuser]
#     queryset = Wallet.objects.all()
#     serializer_class = WalletSerializer

class DriverWalletListView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]
    serializer_class = WalletSerializer

    def get_queryset(self):
        # Filtering users by type "DRIVER" from your custom User model
        return Wallet.objects.filter(user__type=User.Types.DRIVER)


class CustomerWalletListView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]
    serializer_class = WalletSerializer

    def get_queryset(self):
        # Filtering users by type "DRIVER" from your custom User model
        return Wallet.objects.filter(user__type=User.Types.CUSTOMER)

