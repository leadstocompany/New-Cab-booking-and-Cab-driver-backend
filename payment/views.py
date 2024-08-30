from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from trips.models import *
from payment.tasks import  trip_bill_generate_task
import stripe
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from JLP_MyRide import settings
from trips.models import *
from payment.models import *
from payment.serializers import PaymentSerializer
from wallets.models import *
from django.views import View
# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

class TripBilleGeneratedAPIView(APIView):
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        time=request.data.get('time')
        distance=request.data.get('distance')
        waiting_time=request.data.get('waiting_time')
        waiting_charge=request.data.get('waiting_charge')
        total_fare=int(request.data.get('total_fare'))
        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
            trip.time=time
            trip.distance=distance
            trip.waiting_charge=waiting_charge
            trip.waiting_time=waiting_time
            trip.total_fare=total_fare
            trip.save()
            trip_bill_generate_task.delay(trip.id)
            return Response({"detail": "Payment request sent successfully.","payment_type":trip.payment_type, "trip_id":trip.id},  status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)
    

class PaymentQRCodeGenerateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        trip = Trip.objects.get(id=trip_id, driver=request.user)
        total_fare=trip.total_fare
        
      
        if trip.payment_type=="QRCode":
            payment_session= create_payment_session(total_fare * 100, trip)
            payment_instance=Payment.objects.create(trip=trip, amount=total_fare, payment_type=trip.payment_type,payment_status="PENDING", currency="usd", payment_id= payment_session['id'])
            
            return Response({"detail": "Payment urls generate successfully.", "payment_url":payment_session.url, "payment_type":trip.payment_type, "trip_id":trip.id, "peyment_instance": payment_instance},  status=status.HTTP_200_OK)
        else:
             return Response({"detail": "Payment QRCode generate faild."},  status=status.HTTP_200_OK)
    

def create_payment_session(amount, currency='usd'):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': 'Trip Payment',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
    )
   
    return session


class CreatePaymentIntentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')

        try:
            trip = Trip.objects.get(id=trip_id, customer=request.user)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)

        try:
            amount = int(float(amount) * 100)  # Convert to cents
        except ValueError:
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'trip_id': trip_id}
        )

        payment = Payment.objects.create(
            trip=trip,
            amount=amount / 100,
            currency='usd',
            payment_id=payment_intent['id'],
            payment_status="PENDING"
        )

        return Response({
            'client_secret': payment_intent['client_secret'],
            'payment_intent_id': payment_intent['id'],
            'payment_id': payment.id
        }, status=status.HTTP_200_OK)



class WalletPaymentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')

        try:
            trip = Trip.objects.get(id=trip_id, customer=request.user)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found or you are not the customer of this trip."}, status=status.HTTP_404_NOT_FOUND)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        customer=trip.customer
        driver=trip.driver
        if wallet.balance < amount:
            wallet_balance=wallet.balance
            pending_amount=amount - wallet_balance
            wallet.balance = 0
            wallet.save()
            payment = Payment.objects.create(
            trip=trip,
            driver=driver,
            passenger=customer,
            amount=wallet_balance,
            currency='usd',
            payment_status='PAID',
            payment_type='Wallet'
            )
            pending_billed=Payment.objects.create(trip=trip,amount=pending_amount,currency='usd',payment_status='PENDING',driver=driver,passenger=customer)
            # return Response({"detail": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)
            Transaction.objects.create(
                user=driver,
                amount=wallet_balance,
                transaction_type='DEPOSIT',
                remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
            )
            Transaction.objects.create(
                user=customer,
                amount=wallet_balance,
                transaction_type='WITHDRAW',
                remake='Expense wallet money for a Ride booking  from {trip.source} to {trip.destination}'
            )
            driver_wallet=Wallet.objects.get(user=driver)
            driver_wallet.balance +=wallet_balance
            driver_wallet.save()
            pending_bill_data={
                'trip_id':pending_billed.trip.id,
                "trip_source":pending_billed.trip.source,
                "trip_destination":pending_billed.trip.destination,
                "total_rent":pending_billed.trip.total_fare,
                "paid_amount":pending_billed.trip.total_fare-pending_billed.amount,
                "pending_amount":pending_billed.amount,
                "currency":'usd',
                "driver_id":pending_billed.driver.id,
                "passenger":pending_billed.passenger.id
            }
            return Response({"detail": "Payment successful, But some amount Pending", "pending_bill": pending_bill_data}, status=status.HTTP_200_OK)
        else:

            wallet.balance -= amount
            wallet.save()

            payment = Payment.objects.create(
                trip=trip,
                driver=driver,
                passenger=customer,
                amount=amount,
                currency='usd',
                payment_status='PAID',
                payment_type='Wallet'
            )
            Transaction.objects.create(
                    user=driver,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
                )
            Transaction.objects.create(
                    user=customer,
                    amount=amount,
                    transaction_type='WITHDRAW',
                    remake='Expense wallet money for a Ride booking  from {trip.source} to {trip.destination}'
                )
            driver_wallet=Wallet.objects.get(user=driver)
            driver_wallet.balance +=amount
            driver_wallet.save()
            trip.payment_status = 'paid'
            trip.save()
            return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)



class CashPaymentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')

        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found or you are not the customer of this trip."}, status=status.HTTP_404_NOT_FOUND)

        # Assuming amount is validated to be the correct fare
        payment = Payment.objects.create(
            trip=trip,
            amount=amount,
            currency='usd',
            payment_status='PAID',
            payment_type='Cash'
        )

        trip.payment_status = 'paid'
        trip.save()

        return Response({"detail": "Payment marked as completed."}, status=status.HTTP_200_OK)



class StripeWebhookView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return JsonResponse({'status': 'invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'status': 'invalid signature'}, status=400)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            try:
                payment = Payment.objects.get(payment_id=payment_intent['id'])
                payment.payment_status = 'PAID'
                payment.save()
                trip_id = payment.trip.id
                trip = Trip.objects.get(id=trip_id)
                trip.payment_status = 'paid'
                trip.save()
        
                Transaction.objects.create(
                    user=trip.driver,
                    amount=payment.amount,
                    transaction_type='DEPOSIT',
                    remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
                )
                driver_wallet=Wallet.objects.get(user=trip.driver)
                driver_wallet.balance +=payment.amount
                driver_wallet.save()
            except Payment.DoesNotExist:
                pass
        elif event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            try:
                payment = Payment.objects.get(payment_id=session['id'])
                payment.payment_status = 'PAID'
                payment.save()
                trip_id = payment.trip.id
                trip = Trip.objects.get(id=trip_id)
                trip.payment_status = 'paid'
                trip.save()
                
                Transaction.objects.create(
                    user=trip.driver,
                    amount=payment.amount,
                    transaction_type='DEPOSIT',
                    remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
                )
                driver_wallet=Wallet.objects.get(user=trip.driver)
                driver_wallet.balance +=payment.amount
                driver_wallet.save()
            except Payment.DoesNotExist:
                pass
        return JsonResponse({'status': 'success'}, status=200)


class DriverTripIncompletePaymentsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # driver_id = self.kwargs['driver_id']
        incomplete_payment_list=[]
        incomplete_payment_obj=Payment.objects.filter(driver=request.user, payment_status='PENDING') 
        if incomplete_payment_obj:
            for incomplete_payment in incomplete_payment_obj:
                incomplete_payment_data={
                'trip_id':incomplete_payment.trip.id,
                "trip_source":incomplete_payment.trip.source,
                "trip_destination":incomplete_payment.trip.destination,
                "total_rent":incomplete_payment.trip.total_fare,
                "paid_amount":incomplete_payment.trip.total_fare-incomplete_payment.amount,
                "pending_amount":incomplete_payment.amount,
                "currency":'usd',
                "driver_id":incomplete_payment.driver.id,
                "passenger_id":incomplete_payment.passenger.id,
                "driver_name":incomplete_payment.driver.first_name + " "  + incomplete_payment.driver.last_name,
                "driver_phone":incomplete_payment.passenger.phone,
                "passenger_name":incomplete_payment.passenger.first_name + " "  + incomplete_payment.passenger.last_name,
                "driver_name":incomplete_payment.passenger.phone,
                }
                incomplete_payment_list.append(incomplete_payment_data)
        return Response(incomplete_payment_list, status=200)



class PassengerTripPendingBilledView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # driver_id = self.kwargs['driver_id']
    
        pending_bill=Payment.objects.filter(driver=request.user, payment_status='PENDING').first()
        if pending_bill:
            pending_billed_data={
                'trip_id':pending_bill.trip.id,
                "trip_source":pending_bill.trip.source,
                "trip_destination":pending_bill.trip.destination,
                "total_rent":pending_bill.trip.total_fare,
                "paid_amount":pending_bill.trip.total_fare-pending_bill.amount,
                "pending_amount":pending_bill.amount,
                "currency":'usd',
                "driver_id":pending_bill.driver.id,
                "passenger_id":pending_bill.passenger.id,
                "driver_name":pending_bill.driver.first_name + " "  + pending_bill.driver.last_name,
                "driver_phone":pending_bill.passenger.phone,
                "passenger_name":pending_bill.passenger.first_name + " "  + pending_bill.passenger.last_name,
                "driver_name":pending_bill.passenger.phone,
                }
            return Response(pending_billed_data, status=200)
        else:
            return Response({}, status=200)      
                
