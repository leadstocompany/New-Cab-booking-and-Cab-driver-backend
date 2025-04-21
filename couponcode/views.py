from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon, CouponUsage
from .serializers import CouponSerializer, ActiveCouponSerializer, CouponUsageSerializer
from utility.permissions import IsAdminOrSuperuser
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
logger = logging.getLogger(__name__)
# Create your views here.


class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all().order_by('id')
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'code'


class ActiveCouponListView(generics.ListAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = ActiveCouponSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActiveCouponDetailView(generics.RetrieveAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = ActiveCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        coupon_code = self.kwargs.get('code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({'detail': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class CouponDestroyView(generics.DestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'code'


from django.utils import timezone
class ApplyCouponAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        
        coupon_code = request.data.get('code')
        if not coupon_code:
            return Response({'valid': False, 'error': 'Coupon code is required'}, status=400)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({'valid': False, 'error': 'Invalid coupon code'}, status=404)

        if CouponUsage.objects.filter(user=self.request.user, coupon=coupon).exists():
            return Response({'valid': False, 'error': 'You have already used this coupon code'}, status=400)

        elif coupon:
            if coupon.valid_to < timezone.now():
                return Response({'valid': False, 'error': 'Coupon code is expired'}, status=400)
            if coupon.use_count == 0:
                return Response({'valid': False, 'error': 'Coupon code has reached its usage limit'}, status=400)
            # CouponUsage.objects.create(user=self.request.user, coupon=coupon)
            # coupon.use_count -= 1
            # coupon.save()
            return Response({'valid': True, 'discount': coupon.discount})
        else:
            return Response({'valid': False, 'error': 'Coupon code is expired'}, status=400)



class CouponUsageListAPIView(generics.ListAPIView):
    queryset = CouponUsage.objects.all()
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]