from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import math
from django.core.exceptions import ObjectDoesNotExist
from trips.models import *
from payment.tasks import send_payment_confirmation_email, trip_bill_generate_task,trip_payment_complete_task
import stripe
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from JLP_MyRide import settings
from trips.models import *
from payment.models import *
from payment.serializers import PaymentSerializer
from utility.util import get_bill_payment_mapping
from wallets.models import *
from django.views import View
from utility.rating import get_driver_rating
from payment.payment_fcm_notified import fcm_push_notification_trip_bill_generate, fcm_push_notification_trip_payment_complete
import logging
logger = logging.getLogger(__name__)
# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

class TripBilleGeneratedAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        time=request.data.get('time')
        distance=request.data.get('distance')
        # waiting_time=request.data.get('waiting_time')
        # waiting_charge=request.data.get('waiting_charge')
        # total_fare=int(request.data.get('total_fare'))
        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
            base_fare= trip.rent_price
            # Add 5 minutes to the driver's arrival time
            cabbookingprice=CabBookingPrice.objects.get(id=trip.ride_type.id)
            if trip.driver_arrived_at_pickup_time and trip.ride_start_time:
                arrived_time_after_5_min = trip.driver_arrived_at_pickup_time + timedelta(minutes=5)
                # Only calculate waiting time if ride started after the 5 minute grace period
                waiting_time = (
                    trip.ride_start_time - arrived_time_after_5_min
                    if trip.ride_start_time > arrived_time_after_5_min
                    else timedelta(minutes=0)
                )
                # Calculate the waiting time and round to 4 digits
                waiting_time_in_minutes = round(waiting_time.total_seconds() / 60, 2)
                waiting_fare_per_minute=cabbookingprice.waiting_fare_per_minute
                waiting_charge= int(waiting_time_in_minutes) * waiting_fare_per_minute
                total_fare=base_fare + waiting_charge
            else:
                waiting_charge=0
                waiting_time_in_minutes=str(0)
                total_fare= base_fare
            trip.time=time
            trip.distance=distance
            trip.waiting_charge=waiting_charge
            trip.waiting_time= waiting_time_in_minutes
            trip.total_fare=total_fare

            # Calculate the update total fare for schedules trip based on specific cabclass schedule fare percentage
            if trip.scheduled_datetime:
                schedules_trip_fare_total_percentage = cabbookingprice.scheduled_trip_fare_precentage * trip.distance
                trip.total_fare += (base_fare * schedules_trip_fare_total_percentage) / 100

            trip.save()
            # trip_bill_generate_task.delay(trip.id)
            response_data={
                "trip_id":trip.id,
                "source":trip.source,
                "destination":trip.destination,
                "time":trip.time,
                "distance":float(trip.distance),
                "wait_time":trip.waiting_time,
                "wait_charge":float(trip.waiting_charge),
                "base_fare":float(trip.rent_price),
                "total_fare":float(trip.total_fare),
                "payment_status":trip.payment_status,
                "payment_type":trip.payment_type,
                "ride_type_id":trip.ride_type.id,
                "ride_type_name":trip.ride_type.cab_class,
                "customer_id":trip.customer.id,
                "customer_name":trip.customer.first_name + " " + trip.customer.last_name,
                "customer_phone":trip.customer.phone,
                "customer_photo":trip.customer.photo_upload,
                "driver_rating": trip.driver.get_driver_rating(),
            }
            return Response({"detail": "Bill generate successfully.", "trip_bill":response_data},  status=status.HTTP_200_OK)
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)
    
class SendPaymentRequestAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
            fcm_push_notification_trip_bill_generate(trip.id)
            trip_bill_generate_task.delay(trip.id)
            return Response({"detail": "Payment request sent successfully."},  status=status.HTTP_200_OK)
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)
    

class PaymentQRCodeGenerateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        trip = Trip.objects.get(id=trip_id, driver=request.user)
        total_fare=trip.total_fare
        print(total_fare)
      
        if trip.payment_type=="QRCode":
            payment_session= create_payment_session(int(float(total_fare) * 100))
            payment_instance=Bill_Payment.objects.create(trip=trip, amount=total_fare, payment_type=trip.payment_type,payment_status="PENDING", currency="usd", payment_id= payment_session['id'])
            #  return Response({"detail": "Payment urls generate successfully.", "payment_url":payment_session.url, "payment_type":trip.payment_type, "trip_id":trip.id, "peyment_instance": payment_instance},  status=status.HTTP_200_OK)
            return Response({"detail": "Payment urls generate successfully.", "payment_url":payment_session.url},  status=status.HTTP_200_OK)
        else:
             return Response({"detail": "Payment QRCode generate faild."},  status=status.HTTP_200_OK)
    

def create_payment_session(amount):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency':'usd',
                'product_data': {
                    'name': 'Trip Payment',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://example.com/success',
        cancel_url='https://example.com/cancel',
    )
   
    return session


class CreatePaymentIntentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')

        try:
            trip = Trip.objects.get(id=trip_id, customer=request.user)
            driver=trip.driver
            customer=trip.customer
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Trip not found or you are not the driver of this trip."}, status=status.HTTP_404_NOT_FOUND)

        try:
            amount = int(float(amount) * 100)  # Convert to cents
        except ValueError as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={'trip_id': trip_id}
        )
        if Bill_Payment.objects.filter(trip=trip,payment_status="PENDING", amount=amount / 100).exists():
            payment=Bill_Payment.objects.filter(trip=trip,payment_status="PENDING", amount=amount / 100).first()
            payment.payment_id=payment_intent['id']
            payment.save()
        else:
            payment = Bill_Payment.objects.create(
                trip=trip,
                amount=amount / 100,
                currency='usd',
                payment_id=payment_intent['id'],
                payment_status="PENDING",
                payment_type='Online',
                driver=driver,passenger=customer
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
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Trip not found or you are not the customer of this trip."}, status=status.HTTP_404_NOT_FOUND)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        customer=trip.customer
        driver=trip.driver
        if wallet.balance < amount:
            wallet_balance=wallet.balance
            pending_amount=float(amount) - float(wallet_balance)
            wallet.balance = 0
            wallet.save()
            payment = Bill_Payment.objects.create(
            trip=trip,
            driver=driver,
            passenger=customer,
            amount=wallet_balance,
            currency='usd',
            payment_status='PAID',
            payment_type='Wallet'
            )
            pending_billed=Bill_Payment.objects.create(trip=trip,amount=pending_amount,currency='usd',payment_status='PENDING',driver=driver,passenger=customer)
            # return Response({"detail": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)
            Transaction.objects.create(
                user=driver,
                receiver=driver,
                sender=customer,
                amount=wallet_balance,
                transaction_type='INCOME',
                transaction_mode="WALLETS",
                remark=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
            )
            Transaction.objects.create(
                user=customer,
                receiver=driver,
                sender=customer,
                amount=wallet_balance,
                transaction_type='EXPENSE',
                transaction_mode="WALLETS",
                remark=f'Expense wallet money for a Ride booking  from {trip.source} to {trip.destination}'
            )
            driver_wallet=Wallet.objects.get(user=driver)
            driver_wallet.balance +=wallet_balance
            driver_wallet.save()
            pending_bill_data={
                'trip_id':pending_billed.trip.id,
                "trip_source":pending_billed.trip.source,
                "trip_destination":pending_billed.trip.destination,
                "total_rent":pending_billed.trip.total_fare,
                "paid_amount":Decimal(str(pending_billed.trip.total_fare)) - Decimal(str(pending_billed.amount)),
                "pending_amount":pending_billed.amount,
                "currency":'usd',
                "driver_id":pending_billed.driver.id,
                "passenger":pending_billed.passenger.id
            }
            fcm_push_notification_trip_payment_complete(payment.id)
            trip_payment_complete_task.delay(payment.id)
            return Response({"detail": "Payment successful, But some amount Pending", "pending_bill": pending_bill_data}, status=status.HTTP_200_OK)
        else:

            # wallet.balance =  wallet.balance - float(amount)
            wallet.balance -=  Decimal(str(amount))
            wallet.save()

            payment = Bill_Payment.objects.create(
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
                    receiver=driver,
                    sender=customer,
                    amount=amount,
                    transaction_type='INCOME',
                    transaction_mode="WALLETS",
                    remark=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
                )
            Transaction.objects.create(
                    user=customer,
                    receiver=driver,
                    sender=customer,
                    amount=amount,
                    transaction_type='EXPENSE',
                    transaction_mode="WALLETS",
                    remark=f'Expense wallet money for a Ride booking  from {trip.source} to {trip.destination}'
                )
            driver_wallet=Wallet.objects.get(user=driver)
            driver_wallet.balance += Decimal(str(amount))
            driver_wallet.save()
            trip.payment_status = 'paid'
            trip.status = 'COMPLETED'
            trip.save()
            fcm_push_notification_trip_payment_complete(payment.id)
            trip_payment_complete_task(payment.id)
            return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)



class CashPaymentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')
        button_type=request.data.get('button_type')

        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"detail": "Trip not found or you are not the customer of this trip."}, status=status.HTTP_404_NOT_FOUND)

        # Assuming amount is validated to be the correct fare
        # print(payment.passenger.id, "iddi")
        if button_type =="yes":
           
            payment = Bill_Payment.objects.create(
                trip=trip,
                amount=amount,
                driver=trip.driver,
                passenger=trip.customer,
                currency='usd',
                payment_status='PAID',
                payment_type='Cash'
            )

            trip.payment_status = 'paid'
            trip.status = 'COMPLETED'
            trip.save()
            Transaction.objects.create(
                user=trip.driver,
                receiver=trip.driver,
                sender=trip.customer,
                amount=amount,
                transaction_type='INCOME',
                transaction_mode="HANDCASH",
                remark=f'Received Payment by cash for a Ride Trip from {trip.source} to {trip.destination}'
            )
            Transaction.objects.create(
                    user=trip.customer,
                    receiver=trip.driver,
                    sender=trip.customer,
                    amount=amount,
                    transaction_type='EXPENSE',
                    transaction_mode="HANDCASH",
                    remark=f'Expense money throught offline pay cash for a Ride booking  from {trip.source} to {trip.destination}'
                )
            fcm_push_notification_trip_payment_complete(payment.id)
            trip_payment_complete_task.delay(payment.id)
            # trip_payment_complete_task(payment.id)

            return Response({"detail": "Payment marked as completed."}, status=status.HTTP_200_OK)
        else:
            payment = Bill_Payment.objects.create(
                trip=trip,
                driver=trip.driver,
                passenger=trip.customer,
                amount=amount,
                currency='usd',
                payment_status='FAILED',
            )

            trip.payment_status = 'failed'
            trip.status = 'COMPLETED'
            trip.save()
            return Response({"detail": "Payment Failed."}, status=status.HTTP_400_BAD_REQUEST)
        




class UpdateTripPaymentSuccessView(APIView):
    def post(self, request, *args, **kwargs):
        payment_intent_id = request.data.get('payment_intent_id')
        checkout_session_id = request.data.get('checkout_session_id')

        if payment_intent_id:
            return self.handle_payment_intent(payment_intent_id)
        elif checkout_session_id:
            return self.handle_checkout_session(checkout_session_id)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_payment_intent(self, payment_intent_id):
        try:
            # Retrieve PaymentIntent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent['status'] == 'succeeded':

                return self.update_records(payment_intent_id, payment_intent['amount'])
            else:
                return Response({'error': 'Payment intent not succeeded'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def handle_checkout_session(self, checkout_session_id):
        try:
            # Retrieve Checkout Session from Stripe
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            if session['payment_status'] == 'paid':
                return self.update_records(session['id'], session['amount_total'])
            else:
                return Response({'error': 'Checkout session not paid'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update_records(self, payment_id, amount):
        """Update Bill_Payment, Trip, Transaction, and Wallet models."""
        try:
            payment = Bill_Payment.objects.filter(payment_id=payment_id).first()
            payment.payment_status = 'PAID'
            payment.save()

            trip = payment.trip
            trip.payment_status = 'paid'
            trip.status = 'COMPLETED'
            trip.save()

            Transaction.objects.create(
                user=trip.driver,
                receiver=trip.driver,
                sender=trip.customer,
                amount=amount,
                transaction_type='INCOME',
                transaction_mode="WALLETS",
                remark=f'Received Payment for a Ride Trip from {trip.source} to {trip.destination}'
            )
            Transaction.objects.create(
                user=trip.customer,
                receiver=trip.driver,
                sender=trip.customer,
                amount=amount,
                transaction_type='EXPENSE',
                transaction_mode="STRIPEPAY",
                remark=f'Expense money for a Ride Trip from {trip.source} to {trip.destination} throught of stripe payment'
            )
            driver_wallet = Wallet.objects.filter(user=trip.driver).first()
            driver_wallet.balance += amount
            driver_wallet.save()
            fcm_push_notification_trip_payment_complete(payment.id)
            send_payment_confirmation_email.delay(payment.id)
            trip_payment_complete_task.delay(payment.id)
            return JsonResponse({'status': 'success'}, status=200)
        except Bill_Payment.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Trip.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Trip record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Wallet.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': 'Wallet record not found'}, status=status.HTTP_404_NOT_FOUND)

# class StripeWebhookView(APIView):
#     @method_decorator(csrf_exempt)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#         event = None

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_FOR_RIDE_PAYMENT
#             )
#         except ValueError:
#             return JsonResponse({'status': 'invalid payload'}, status=400)
#         except stripe.error.SignatureVerificationError:
#             return JsonResponse({'status': 'invalid signature'}, status=400)

#         if event['type'] == 'payment_intent.succeeded':
#             payment_intent = event['data']['object']
#             try:
#                 payment = Bill_Payment.objects.get(payment_id=payment_intent['id'])
#                 payment.payment_status = 'PAID'
#                 payment.save()
#                 trip_id = payment.trip.id
#                 trip = Trip.objects.get(id=trip_id)
#                 trip.payment_status = 'paid'
#                 trip.save()
        
#                 Transaction.objects.create(
#                     user=trip.driver,
#                     amount=payment.amount,
#                     transaction_type='DEPOSIT',
#                     remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
#                 )
#                 driver_wallet=Wallet.objects.get(user=trip.driver)
#                 driver_wallet.balance +=payment.amount
#                 driver_wallet.save()
#             except Bill_Payment.DoesNotExist:
#                 pass
#         elif event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             try:
#                 payment = Bill_Payment.objects.get(payment_id=session['id'])
#                 payment.payment_status = 'PAID'
#                 payment.save()
#                 trip_id = payment.trip.id
#                 trip = Trip.objects.get(id=trip_id)
#                 trip.payment_status = 'paid'
#                 trip.save()
                
#                 Transaction.objects.create(
#                     user=trip.driver,
#                     amount=payment.amount,
#                     transaction_type='DEPOSIT',
#                     remake=f'Receive Payment for a Ride Trip from {trip.source} to {trip.destination}'
#                 )
#                 driver_wallet=Wallet.objects.get(user=trip.driver)
#                 driver_wallet.balance +=payment.amount
#                 driver_wallet.save()
#             except Bill_Payment.DoesNotExist:
#                 pass
#         return JsonResponse({'status': 'success'}, status=200)


class DriverTripIncompletePaymentsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # driver_id = self.kwargs['driver_id']
        incomplete_payment_list=[]
        incomplete_trip_bill_obj=Trip.objects.filter(status='COMPLETED',driver=request.user).exclude(payment_status='paid')
        # incomplete_payment_obj=Bill_Payment.objects.filter(driver=request.user, payment_status='PENDING') 
        for incomplete_trip_bill in incomplete_trip_bill_obj:
            incomplete_payment=Bill_Payment.objects.filter(trip=incomplete_trip_bill, payment_status__in=['PENDING', 'FAILED']).first()
            if incomplete_payment:
                incomplete_payment_data={
                'trip_id':incomplete_payment.trip.id,
                "trip_source":incomplete_payment.trip.source,
                "trip_destination":incomplete_payment.trip.destination,
                "total_fare":incomplete_payment.trip.total_fare,
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
            else:
                incomplete_payment_data={
                'trip_id':incomplete_trip_bill.id,
                "trip_source":incomplete_trip_bill.source,
                "trip_destination":incomplete_trip_bill.destination,
                "total_fare":incomplete_trip_bill.total_fare,
                "paid_amount":0,
                "pending_amount":incomplete_trip_bill.total_fare,
                "currency":'usd',
                "driver_id":incomplete_trip_bill.driver.id,
                "passenger_id":incomplete_trip_bill.customer.id,
                "driver_name":incomplete_trip_bill.driver.first_name + " "  + incomplete_trip_bill.driver.last_name,
                "driver_phone":incomplete_trip_bill.customer.phone,
                "passenger_name":incomplete_trip_bill.customer.first_name + " "  + incomplete_trip_bill.customer.last_name,
                "driver_name":incomplete_trip_bill.customer.phone,
                }
            incomplete_payment_list.append(incomplete_payment_data)
        return Response(incomplete_payment_list, status=200)



class PassengerTripPendingBilledView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # driver_id = self.kwargs['driver_id']
        trip_bill=Trip.objects.filter(status='COMPLETED', customer=request.user).exclude(payment_status='paid').first()
        pending_bill=Bill_Payment.objects.filter(customer=request.user, payment_status__in=['PENDING', 'FAILED']).first()
        
        if trip_bill:
            pending_bill={
            "trip_id":trip_bill.id,
            "source":trip_bill.source,
            "destination":trip_bill.destination,
            "time" :trip_bill.time,
            "distance":trip_bill.distance,
            "base_fare":trip_bill.rent_price,
            "waiting_charge":trip_bill.waiting_charge,
            "waiting_time":trip_bill.waiting_time,
            "total_fare":trip_bill.total_fare,
            "payment_type":trip_bill.payment_type,
            "ride_type":trip_bill.ride_type,
            "driver_id":trip_bill.driver.id,
            "driver_name":trip_bill.driver.first_name + " " + trip_bill.driver.last_name,
            "driver_phone":trip_bill.driver.phone,
            }
            return Response(pending_billed_data, status=200, hint="trip_bill")
        elif pending_bill:
            pending_billed_data={
                'trip_id':pending_bill.trip.id,
                "trip_source":pending_bill.trip.source,
                "trip_destination":pending_bill.trip.destination,
                "total_rent":pending_bill.trip.total_fare,
                "paid_amount":pending_bill.trip.total_fare - pending_bill.amount,
                "pending_amount":pending_bill.amount,
                "currency":'usd',
                "driver_id":pending_bill.driver.id,
                "passenger_id":pending_bill.passenger.id,
                "driver_name":pending_bill.driver.first_name + " "  + pending_bill.driver.last_name,
                "driver_phone":pending_bill.passenger.phone,
                "passenger_name":pending_bill.passenger.first_name + " "  + pending_bill.passenger.last_name,
                "driver_name":pending_bill.passenger.phone,
                }
            return Response(pending_billed_data, status=status.HTTP_200_OK, hint="pending_bill")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, hint="no_bill")      

class AvailablePlaceholdersView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        _, placeholders = get_bill_payment_mapping(1, get_key=True)
        return Response((list(placeholders.keys())), status=200)