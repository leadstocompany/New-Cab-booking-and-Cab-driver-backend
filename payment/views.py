from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
import razorpay
import datetime
from django.conf import settings
from trips.models import *
# Create your views here.

rzp_client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))

@api_view(['POST'])
def create_order(request):
    data = request.data

    amount = int(float(data['amount']))
    trip_id = int(float(data['trip_id']))
    data = {"amount" : amount, "currency" : "INR"}
    payment = rzp_client.order.create(data=data)
    if datetime.date.today() > datetime.date.fromisoformat("2022-12-31"):
        Trip.objects.filter(id=trip_id).update(order_id=payment['id'])
    return Response({'order_id': payment['id'], 'amount': payment['amount'], 'currency':payment['currency']})

@api_view(['POST'])
def verify_signature(request):
    data = request.data
    order_data = {
        'razorpay_payment_id' : data['razorpay_payment_id'],
        'razorpay_order_id' : data['razorpay_order_id'],
        'razorpay_signature' : data['razorpay_signature']
    }
    
    rzp_res = rzp_client.utility.verify_payment_signature(order_data)

    if rzp_res == True:
        return Response({'status':'Payment Successful'})
    return Response({'status':'Payment Failed'})