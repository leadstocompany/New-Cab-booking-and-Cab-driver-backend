from django.shortcuts import render
from rest_framework import generics, permissions, status
from .models import Subscription, Subscriptions_Logs, SubscriptionPlan
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionsLogsSerializer
from utility.permissions import IsAdminOrSuperuser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import Driver
from JLP_MyRide import settings
import stripe
from datetime import datetime


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
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionsLogsListAPIView(generics.ListAPIView):
    queryset = Subscriptions_Logs.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    permission_classes = [IsAdminOrSuperuser]


class SubscriptionsLogsUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Subscriptions_Logs.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrSuperuser]

class SubscriptionListAPIView(generics.ListAPIView):
    queryset = Subscriptions_Logs.objects.all()
    serializer_class = SubscriptionsLogsSerializer
    permission_classes = [IsAdminOrSuperuser]


class SubscriptionUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrSuperuser]

class SubscriptionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, driver_id, plan_id):
        driver = get_object_or_404(Driver, id=driver_id)
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        token = request.data.get('stripeToken')

        if not token:
            return Response({"error": "Stripe token is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # Stripe payment logic
        try:
            charge = stripe.Charge.create(
                amount=int(plan.price * 100),  # Amount in cents
                currency="usd",
                source=token,
                description=f"Charge for {driver.username} - Subscription Plan {plan.id}"
            )

            payment_status = 'PAID' if charge['status'] == 'succeeded' else 'FAILED'
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the driver already has an subscription
        subscription = Subscription.objects.filter(driver=driver).first()
        if subscription:
            if payment_status == 'PAID' and charge['status'] == 'succeeded': 
                subscription.plan = plan
                subscription.pay_amount = plan.price
                subscription.payment_status = payment_status
                subscription.number_of_time_subscribe +=1
                subscription.is_active=True
                subscription.pending_rides +=plan.number_of_rides
                subscription.payment_id=charge['id'],
                subscription.updated_at=datetime.now()
                subscription.save()
        else:
            # Create Subscription and Log
            if payment_status == 'PAID' and charge['status'] == 'succeeded': 
                subscription = Subscription.objects.create(
                    driver=driver,
                    plan=plan,
                    pay_amount=plan.price,
                    payment_status=payment_status,
                    number_of_time_subscribe=1,
                    pending_rides =plan.number_of_rides,
                    payment_id=charge['id'],
                    is_active=True,

                )

        Subscriptions_Logs.objects.create(
            driver=driver,
            plan=plan,
            pay_amount=plan.price,
            payment_status=payment_status,
            payment_id=charge['id'],
            is_active=True,
        )

        serializer = SubscriptionSerializer(subscription)
        return Response({"data":serializer.data,payment_status:charge['status']}, status=status.HTTP_201_CREATED)





class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        driver_id = self.kwargs['driver_id']
        return Subscription.objects.get(driver__id=driver_id)