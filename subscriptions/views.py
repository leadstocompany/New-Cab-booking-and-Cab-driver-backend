from django.shortcuts import render
from rest_framework import generics, permissions, status
from .models import Subscriptions, Subscription_Logs, SubscriptionPlan
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionsLogsSerializer
from utility.permissions import IsAdminOrSuperuser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import Driver
from JLP_MyRide import settings
import stripe
from datetime import datetime, timedelta
# from django.utils.timezone import now
from django.utils import timezone
from rest_framework.exceptions import NotFound
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger(__name__)

# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionPlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrSuperuser]
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

class SubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrSuperuser]
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class ActiveSubscriptionPlanListView(generics.ListAPIView):
    # queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        # Check if the driver has any vehicles
        vehicle = user.vehicles.first()
        if not vehicle:
            return SubscriptionPlan.objects.none()  # or handle the case appropriately

        vehicle_class = vehicle.cab_class
        queryset = SubscriptionPlan.objects.filter(is_active=True, vehicle_class=vehicle_class)
        return queryset

class SubscriptionsLogsListAPIView(generics.ListAPIView):
    queryset = Subscription_Logs.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    permission_classes = [IsAdminOrSuperuser]


class SubscriptionsLogsUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Subscription_Logs.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrSuperuser]

class SubscriptionListAPIView(generics.ListAPIView):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminOrSuperuser]

class ActiveSubscriptionListAPIView(generics.ListAPIView):
    serializer_class = SubscriptionsLogsSerializer
    permission_classes = [IsAdminOrSuperuser]

    def get_queryset(self):
        """
        This view returns a list of all active subscriptions.
        A subscription is considered active if its expire_date is in the future.
        """
        return Subscriptions.objects.filter(expire_date__gt=timezone.localtime(timezone.now()), is_active=True)

class ExpiredSubscriptionListAPIView(generics.ListAPIView):
    # queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    permission_classes = [IsAdminOrSuperuser]
    def get_queryset(self):
        """
        Optionally restricts the returned subscriptions to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        return Subscriptions.objects.filter(expire_date__lte=timezone.localtime(timezone.now()))

class SubscriptionUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrSuperuser]



# class SubscriptionDetailView(generics.RetrieveAPIView):
#     serializer_class = SubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         driver_id = self.kwargs['driver_id']
#         driver=Driver.objects.get(id=driver_id)
#         return Subscriptions.objects.filter(driver=driver)
    




class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            driver_id = self.kwargs['driver_id']
            driver = Driver.objects.get(id=driver_id)
            
            # Assuming each driver has only one Subscription, or you want to get a specific one
            subscription = Subscriptions.objects.get(driver=driver)
            return subscription
        except Driver.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            raise NotFound(detail="Driver not found.")
        except Subscriptions.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            raise NotFound(detail="Subscription not found.")
        


# class SubscriptionDetailView(generics.ListAPIView):
#     serializer_class = SubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         driver_id = self.kwargs['driver_id']
#         driver = Driver.objects.get(id=driver_id)
        
#         # Return all subscriptions related to the driver
#         return Subscriptions.objects.filter(driver=driver)


class SubscriptionPaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, driver_id, plan_id):
        driver = get_object_or_404(Driver, id=driver_id)
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
     
        try:
            plan_price=plan.price
            amount = int(float(plan_price) * 100) 

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method_types=['card']
            )
            subscription = Subscriptions.objects.filter(driver=driver).first()
            if not subscription:
                subscription = Subscriptions.objects.create(
                    driver=driver,
                    plan=plan,
                    pay_amount=plan.price,
                    payment_status="PENDING",
                    number_of_time_subscribe=0,
                    subcribe_date =timezone.localtime(timezone.now()),
                    expire_date =timezone.localtime(timezone.now()) + timedelta(days=int(plan.days)),
                    payment_id=payment_intent['id'],
                    is_active=True,)
            Subscription_Logs.objects.create(
            driver=driver,
            plan=plan,
            pay_amount=plan.price,
            subcribe_date =timezone.localtime(timezone.now()),
            expire_date = timezone.localtime(timezone.now()) + timedelta(days=int(plan.days)),
            payment_status="PENDING",
            payment_id=payment_intent['id'],
            is_active=True,
            )

            return Response({
                'client_secret': payment_intent['client_secret'],
                'payment_intent_id': payment_intent['id'],
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UpdateSubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        try:
            # Fetch payment intent details from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent['status'] == 'succeeded':
                try:
                    subscription_log = Subscription_Logs.objects.filter(payment_id=payment_intent_id, driver=self.request.user).first()
                    print(subscription_log.payment_id, "=", payment_intent_id)
                    subscription_log.payment_status = 'PAID'
                    subscription_log.save()
                    subscription=Subscriptions.objects.filter(driver=subscription_log.driver).first()
                    subscription_plan=SubscriptionPlan.objects.get(id=subscription_log.plan.id)
                    subscription.plan = subscription_plan
                    subscription.pay_amount = subscription_log.pay_amount
                    subscription.payment_status = 'PAID'
                    subscription.number_of_time_subscribe +=1
                    subscription.subcribe_date = subscription_log.subcribe_date
                    subscription.expire_date = subscription_log.expire_date
                    subscription.payment_id = payment_intent['id']
                    subscription.save() 
                    return JsonResponse({'status': 'success'}, status=200)
                except Subscription_Logs.DoesNotExist:
                    return JsonResponse({'massage': 'Subscrition doesnot exist'}, status=400)
            else:
                return JsonResponse({'status': 'Failed'}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return JsonResponse({'massage': str(e)}, status=400)
            




# class DriverSubscriptionStripeWebhookView(APIView):
#     @method_decorator(csrf_exempt)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#         event = None

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_FOR_SUBSCRIPTIONS
#             )
#         except ValueError:
#             return JsonResponse({'status': 'invalid payload'}, status=400)
#         except stripe.error.SignatureVerificationError:
#             return JsonResponse({'status': 'invalid signature'}, status=400)

#         if event['type'] == 'payment_intent.succeeded':
#             payment_intent = event['data']['object']
#             try:
#                 subscription_log = Subscription_Logs.objects.get(payment_id=payment_intent['id'])
#                 subscription_log.payment_status = 'PAID'
#                 subscription_log.save()
#                 subscription=Subscriptions.objects.filter(driver=subscription_log.driver).first()
#                 subscription.plan=subscription_log.plan,
#                 subscription.pay_amount=subscription_log.pay_amount,
#                 subscription.payment_status='PAID',
#                 subscription.number_of_time_subscribe +=1,
#                 subscription.subcribe_date =subscription_log.subcribe_date,
#                 subscription.expire_date = subscription_log.expire_date,
#                 subscription.payment_id=payment_intent['id'],
#                 subscription.save() 
#                 return JsonResponse({'status': 'success'}, status=200)
#             except Subscription_Logs.DoesNotExist:
#                 return JsonResponse({'massage': 'Subscrition doesnot exist'}, status=400)
#         else:
#             return JsonResponse({'status': 'Failed'}, status=400)
           
