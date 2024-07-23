from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from trips.models import *
from trips.tasks import  payment_request_notified
import stripe
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from JLP_MyRide import settings
from trips.models import *
from payment.models import *
from wallets.models import *
from django.views import View
# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY
class PaymentRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

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
        except Trip.DoesNotExist:
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)
    
        payment_request_notified.delay(trip)
        
        if trip.payment_type=="Cash":
            return Response({"detail": "Payment request sent successfully.","payment_type":trip.payment_type, "trip_id":trip.id},  status=status.HTTP_200_OK)
        elif trip.payment_type=="Wallet":
            return Response({"detail": "Payment request sent successfully.","payment_type":trip.payment_type, "trip_id":trip.id},  status=status.HTTP_200_OK)
        elif trip.payment_type=="UPI":
            #  payment_url = create_payment_session(total_fare * 100, trip)
            return Response({"detail": "Payment request sent successfully.",  "payment_type":trip.payment_type, "trip_id":trip.id,},  status=status.HTTP_200_OK)
        elif trip.payment_type=="QRCode":
            payment_session= create_payment_session(total_fare * 100, trip)
            payment_instance=Payment.objects.create(trip=trip, amount=total_fare, payment_type=trip.payment_type,payment_status="PENDING", currency="usd", payment_id= payment_session['id'])
            return Response({"detail": "Payment request sent successfully.", "payment_url":payment_session.url, "payment_type":trip.payment_type, "trip_id":trip.id, "peyment_instance": payment_instance,},  status=status.HTTP_200_OK)
        else:
             return Response({"detail": "Payment request sent faild."},  status=status.HTTP_200_OK)
    

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

        if wallet.balance < amount:
            return Response({"detail": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= amount
        wallet.save()

        payment = Payment.objects.create(
            trip=trip,
            amount=amount,
            currency='usd',
            payment_status='PAID',
            payment_type='Wallet'
        )

        trip.payment_status = 'paid'
        trip.save()
        customer=trip.customer
        driver=trip.driver
        Transaction.objects.create(
                user=driver,
                amount=amount,
                transaction_type='DEPOSIT',
                remake='Receive Payment for a Ride Trip'
            )
        Transaction.objects.create(
                user=customer,
                amount=amount,
                transaction_type='WITHDRAW',
                remake='Expense wallet money  for a Ride booking'
            )
        driver_wallet=Wallet.objects.get(user=driver)
        driver_wallet +=amount
        driver.save()
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



# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         return JsonResponse({'status': 'invalid payload'}, status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return JsonResponse({'status': 'invalid signature'}, status=400)

#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']
#         try:
#             payment = Payment.objects.get(payment_id=payment_intent['id'])
#             payment.payment_status = 'PAID'
#             payment.save()
#             trip_id=payment.trip.id
#             trip=Trip.objects.get(id=trip_id)
#             trip.payment_status = 'paid'
#             trip.save()
#         except Payment.DoesNotExist:
#             pass
#     elif event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         payment = Payment.objects.get(payment_id=session['id'])
#         payment.payment_status = 'PAID'
#         payment.save()
#         trip_id=payment.trip.id
#         trip=Trip.objects.get(id=trip_id)
#         trip.payment_status = 'paid'
#         trip.save()
#     return JsonResponse({'status': 'success'}, status=200)
class StripeWebhookView(View):
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
            except Payment.DoesNotExist:
                pass
        elif event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment = Payment.objects.get(payment_id=session['id'])
            payment.payment_status = 'PAID'
            payment.save()
            trip_id = payment.trip.id
            trip = Trip.objects.get(id=trip_id)
            trip.payment_status = 'paid'
            trip.save()

        return JsonResponse({'status': 'success'}, status=200)
